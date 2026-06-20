import logging

from .models import FAMILY_CSV_HEADER, Person
from .services import WHERE_PARENTS, BaseService, build_parent_criteria
from .utils import clean_address, is_valid_tc


class FamilyService(BaseService):
    def __init__(self):
        self._person_cache: dict[str, Person] = {}

    def get_full_person(self, tc: str) -> Person | None:
        if not is_valid_tc(tc):
            return None

        if tc in self._person_cache:
            return self._person_cache[tc]

        with self._get_connection("FULLDATA") as conn:
            if not conn:
                return None
            res = self.execute_query_with_conn(
                conn, "SELECT * FROM `109m` WHERE TC = %s", (tc,)
            )
            if not res:
                return None

            p = Person.from_dict(res[0])

        addr_res = self.execute_query(
            "ADRESSDATA", "SELECT GUNCELADRES FROM adresv2 WHERE TC = %s", (tc,)
        )
        p.GUNCELADRES = clean_address(addr_res[0]["GUNCELADRES"]) if addr_res else ""
        p.GSM_LIST = self._fetch_gsm_numbers(tc)

        self._person_cache[tc] = p
        return p

    def _fetch_gsm_numbers(self, tc: str) -> list[str]:
        try:
            res = self.execute_query(
                "GSMDATA", "SELECT GSM FROM `140gsm` WHERE TC = %s", (tc,)
            )
            return [str(row["GSM"]) for row in res if row["GSM"]]
        except Exception as e:
            logging.debug(f"GSM çekme hatası ({tc}): {e}")
            return []

    def get_relatives(self, criteria: str, params: tuple) -> list[Person]:
        res = self.execute_query(
            "FULLDATA", f"SELECT * FROM `109m` WHERE {criteria}", params
        )

        uncached_tcs = [
            str(r["TC"]) for r in res if str(r["TC"]) not in self._person_cache
        ]
        addr_map: dict[str, str] = {}
        gsm_map: dict[str, list[str]] = {}

        if uncached_tcs:
            placeholders = ",".join(["%s"] * len(uncached_tcs))
            addr_res = self.execute_query(
                "ADRESSDATA",
                f"SELECT TC, GUNCELADRES FROM adresv2 WHERE TC IN ({placeholders})",
                tuple(uncached_tcs),
            )
            addr_map = {str(r["TC"]): r["GUNCELADRES"] for r in addr_res}

            gsm_res = self.execute_query(
                "GSMDATA",
                f"SELECT TC, GSM FROM `140gsm` WHERE TC IN ({placeholders})",
                tuple(uncached_tcs),
            )
            for r in gsm_res:
                tc = str(r["TC"])
                if r["GSM"]:
                    gsm_map.setdefault(tc, []).append(str(r["GSM"]))

        relatives = []
        for r in res:
            tc = str(r["TC"])
            if tc in self._person_cache:
                relatives.append(self._person_cache[tc])
                continue
            p = Person.from_dict(r)
            p.GUNCELADRES = (
                clean_address(addr_map.get(tc, "")) if tc in addr_map else ""
            )
            p.GSM_LIST = gsm_map.get(tc, [])
            self._person_cache[tc] = p
            relatives.append(p)
        return relatives

    def _log_gsm_info(self, person: Person):
        if person.GSM:
            logging.info(f"    [109M Verisi] GSM: {person.GSM}")
        if person.GSM_LIST:
            extra_gsms = [g for g in person.GSM_LIST if g != person.GSM]
            if extra_gsms:
                logging.info(
                    f"    [GSMDATA Ek Veri] Numaralar: {', '.join(extra_gsms)}"
                )

    def _fetch_ancestors(self, main_p: Person, results: list) -> list:
        parent_tcs = [(main_p.ANNETC, "Anne"), (main_p.BABATC, "Baba")]
        parent_tcs = [(tc, label) for tc, label in parent_tcs if is_valid_tc(tc)]
        if not parent_tcs:
            return []

        all_tcs = [tc for tc, _ in parent_tcs]

        ph = ",".join(["%s"] * len(all_tcs))
        parent_data = self.execute_query(
            "FULLDATA",
            f"SELECT TC, ANNETC, BABATC FROM `109m` WHERE TC IN ({ph})",
            tuple(all_tcs),
        )
        parent_map: dict[str, dict] = {r["TC"]: r for r in parent_data}
        for r in parent_data:
            for gt_tc in [r["ANNETC"], r["BABATC"]]:
                if is_valid_tc(gt_tc):
                    all_tcs.append(gt_tc)

        if not all_tcs:
            return []

        ph2 = ",".join(["%s"] * len(all_tcs))
        res = self.execute_query(
            "FULLDATA",
            f"SELECT * FROM `109m` WHERE TC IN ({ph2})",
            tuple(all_tcs),
        )

        uncached = [str(r["TC"]) for r in res if str(r["TC"]) not in self._person_cache]
        addr_map, gsm_map = self._batch_fetch_details(uncached)

        person_map: dict[str, Person] = {}
        for r in res:
            p = self._resolve_person(r, addr_map, gsm_map)
            person_map[p.TC] = p

        parents = []
        for tc, label in parent_tcs:
            if tc not in person_map:
                continue
            p = person_map[tc]
            results.append((label, p))
            parents.append((p.TC, label))
            logging.info(f"--- {label} bulundu: {p.AD} {p.SOYAD}")

            if tc not in parent_map:
                continue
            for gt_tc, gt_label in [
                (parent_map[tc]["ANNETC"], f"Anneanne({label})"),
                (parent_map[tc]["BABATC"], f"Dede({label})"),
            ]:
                if is_valid_tc(gt_tc) and gt_tc in person_map:
                    gp = person_map[gt_tc]
                    results.append((gt_label, gp))
                    logging.info(f"  --- {gt_label} bulundu: {gp.AD} {gp.SOYAD}")

        return parents

    def generate_tree(self, main_tc: str) -> str:
        self._person_cache.clear()
        main_p = self.get_full_person(main_tc)
        if not main_p:
            return "Kayıt bulunamadı."

        logging.info(
            f"!!! Soy ağacı oluşturuluyor: {main_p.AD} {main_p.SOYAD} ({main_tc})"
        )
        self._log_gsm_info(main_p)

        results = [("Ana Kayıt", main_p)]

        logging.info(">>> Üst soylar çekiliyor...")
        parents = self._fetch_ancestors(main_p, results)

        logging.info(">>> Kardeşler ve yeğenler çekiliyor...")
        self._add_siblings(results, main_p)

        logging.info(">>> Çocuklar çekiliyor...")
        self._add_children(results, main_p)

        logging.info(">>> Geniş aile çekiliyor...")
        for p_tc, p_label in parents:
            logging.info(f"[{p_label}] tarafı geniş aile aranıyor...")
            self._add_extended(results, p_tc, p_label)

        filename = f"./index/{main_p.AD}_{main_p.SOYAD}.csv"
        logging.info(f"Dosya kaydediliyor: {filename}")
        rows = [r[1].to_csv_row(r[0]) for r in results]
        self.save_to_csv(filename, FAMILY_CSV_HEADER, rows)
        logging.info(f"!!! İşlem Tamamlandı. Toplam {len(results)} kayıt yazıldı.")
        return f"Kaydedildi: {filename}"

    def _get_children_by_parents(self, parent_tcs: list) -> dict[str, list[Person]]:
        if not parent_tcs:
            return {}
        placeholders = ",".join(["%s"] * len(parent_tcs))
        res = self.execute_query(
            "FULLDATA",
            f"SELECT * FROM `109m` WHERE ANNETC IN ({placeholders}) OR BABATC IN ({placeholders})",
            tuple(parent_tcs) * 2,
        )
        uncached_tcs = [
            str(r["TC"]) for r in res if str(r["TC"]) not in self._person_cache
        ]
        addr_map, gsm_map = self._batch_fetch_details(uncached_tcs)

        grouped: dict[str, list[Person]] = {}
        parent_set = set(parent_tcs)
        for r in res:
            p = self._resolve_person(r, addr_map, gsm_map)
            parent_tc = p.ANNETC if p.ANNETC in parent_set else p.BABATC
            grouped.setdefault(parent_tc, []).append(p)
        return grouped

    def _batch_fetch_details(
        self, tcs: list
    ) -> tuple[dict[str, str], dict[str, list[str]]]:
        addr_map: dict[str, str] = {}
        gsm_map: dict[str, list[str]] = {}
        if not tcs:
            return addr_map, gsm_map
        ph = ",".join(["%s"] * len(tcs))
        addr_res = self.execute_query(
            "ADRESSDATA",
            f"SELECT TC, GUNCELADRES FROM adresv2 WHERE TC IN ({ph})",
            tuple(tcs),
        )
        addr_map = {str(r["TC"]): r["GUNCELADRES"] for r in addr_res}
        gsm_res = self.execute_query(
            "GSMDATA", f"SELECT TC, GSM FROM `140gsm` WHERE TC IN ({ph})", tuple(tcs)
        )
        for r in gsm_res:
            tc = str(r["TC"])
            if r["GSM"]:
                gsm_map.setdefault(tc, []).append(str(r["GSM"]))
        return addr_map, gsm_map

    def _resolve_person(self, row: dict, addr_map: dict, gsm_map: dict) -> Person:
        tc = str(row["TC"])
        if tc in self._person_cache:
            return self._person_cache[tc]
        p = Person.from_dict(row)
        p.GUNCELADRES = clean_address(addr_map.get(tc, "")) if tc in addr_map else ""
        p.GSM_LIST = gsm_map.get(tc, [])
        self._person_cache[tc] = p
        return p

    def _add_siblings(self, results: list, person: Person):
        criteria, params = build_parent_criteria(person)
        if not criteria:
            return

        siblings = self.get_relatives(criteria, tuple(params))
        if not siblings:
            return

        logging.info(f"Kardeşler listeleniyor ({len(siblings)} kişi bulundu):")
        children_map = self._get_children_by_parents([s.TC for s in siblings])

        for s in siblings:
            results.append((self._sibling_label(s, person), s))
            logging.info(f"  - {results[-1][0]}: {s.AD} {s.SOYAD} ({s.TC})")
            s_children = children_map.get(s.TC, [])
            if s_children:
                logging.info(
                    f"    * {s.AD} kişisinin {len(s_children)}lüğü (yeğen) bulundu."
                )
                for c in s_children:
                    results.append(("Yeğen", c))

    def _sibling_label(self, sibling: Person, person: Person) -> str:
        gender = "Erkek" if sibling.CINSIYET == "Erkek" else "Kız"
        label = f"{gender} Kardeş"
        is_step = sibling.ANNETC != person.ANNETC or sibling.BABATC != person.BABATC
        return f"{label} (Üvey)" if is_step else label

    def _add_children(self, results: list, person: Person):
        if not is_valid_tc(person.TC):
            return
        children = self.get_relatives(WHERE_PARENTS, (person.TC, person.TC))
        if not children:
            return

        child_tcs = [c.TC for c in children]
        grandchildren_map = (
            self._get_children_by_parents(child_tcs) if child_tcs else {}
        )

        logging.info(f"Çocuklar listeleniyor ({len(children)} kişi bulundu):")
        for c in children:
            label = "Oğlu" if c.CINSIYET == "Erkek" else "Kızı"
            logging.info(f"  - {label}: {c.AD} {c.SOYAD}")
            results.append((label, c))
            c_children = grandchildren_map.get(c.TC, [])
            if c_children:
                logging.info(
                    f"    * {c.AD} {c.SOYAD}'in {len(c_children)} çocuğu bulundu."
                )
                for gc in c_children:
                    results.append((f"{c.AD} {c.SOYAD}'in Çocuğu", gc))

    def _get_extended_label(self, p_label: str, gender: str) -> str:
        if p_label == "Baba":
            return "Amca" if gender == "Erkek" else "Hala"
        return "Dayı" if gender == "Erkek" else "Teyze"

    def _add_extended(self, results: list, p_tc: str, p_label: str):
        parent = self.get_full_person(p_tc)
        if not parent:
            return

        criteria, params = build_parent_criteria(parent)
        if not criteria:
            return

        relatives = self.get_relatives(criteria, tuple(params))
        if not relatives:
            return

        logging.info(f"  {p_label} tarafı kardeşleri ({len(relatives)} kişi bulundu):")
        children_map = self._get_children_by_parents([r.TC for r in relatives])

        for r in relatives:
            results.append((self._get_extended_label(p_label, r.CINSIYET), r))
            logging.info(f"    - {results[-1][0]}: {r.AD} {r.SOYAD} ({r.TC})")
            r_children = children_map.get(r.TC, [])
            if r_children:
                logging.info(
                    f"      + {r.AD} kişisinin {len(r_children)} çocuğu (kuzen) bulundu."
                )
                for c in r_children:
                    results.append(("Kuzen", c))
