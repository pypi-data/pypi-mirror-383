import io

import polars as pl

from mobisurvstd.common.persons import clean

SCHEMA = {
    "PP1": pl.UInt8,  # Code fichier = 2 (personne)
    "PMET": pl.UInt8,  # Méthode d'enquête du ménage (EMC2 only)
    "IDP3": pl.UInt16,  # Année de fin d'enquête
    "IDP4": pl.String,  # Code Insee ville centre
    "ZFP": pl.String,  # Zone fine de résidence
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "PER": pl.UInt8,  # Numéro de personne
    "GP1": pl.String,  # Insee Zone fine du lieu de résidence de la personne
    "STP": pl.String,  # Secteur de tirage dans l’enquête d’origine (résidence)
    "AN": pl.UInt16,  # Année du jour d’enquête (EMC2)
    "ANNEE": pl.UInt16,  # Année du jour d’enquête (EDGT, EDVM, EMD)
    "MOIS": pl.UInt8,  # Mois du jour d’enquête
    "DATE": pl.UInt8,  # Jour d’enquête
    "JOUR": pl.UInt8,  # Jour des déplacements
    "PENQ": pl.UInt8,  # Personne enquêtée ?
    "P2": pl.UInt8,  # Sexe de la personne
    "P3": pl.UInt8,  # Lien avec la personne de référence
    "P4": pl.UInt8,  # Âge de la personne
    "P5": pl.UInt8,  # Possession d'un téléphone portable
    "P6": pl.UInt8,  # Possession d'une adresse de messagerie électronique
    "P7": pl.UInt8,  # Possession du permis de conduire voiture
    "P8": pl.UInt8,  # Niveau d’études
    "P9": pl.UInt8,  # Occupation principale de la personne
    "P10": pl.UInt8,  # Occupation secondaire
    "PCSC": pl.UInt8,  # PCS courte
    "PCSD": pl.UInt8,  # PCS détaillée
    "P12": pl.UInt8,  # Possession d'un abonnement TC valide hier
    "P14": pl.UInt8,  # Travail, études à domicile
    "P15": pl.String,  # Zone fine du lieu de travail ou d’études
    "DP15": pl.Float64,  # Distance domicile - travail / études à vol d'oiseau
    "GP5": pl.String,  # Insee Zone fine du lieu de travail / études
    "STW": pl.String,  # Secteur de tirage dans l’enquête d’origine (lieu de travail / études)
    "P16": pl.UInt8,  # Disposition d'une VP pour se rendre sur le lieu de travail ou d'études
    "P13B": pl.UInt8,  # Pratique du télétravail (EMC2 only)
    "P17": pl.UInt8,  # Problèmes de stationnement sur le lieu de travail ou d'études (EDGT, EDVM, EMD)
    "P18": pl.UInt8,  # Difficultés de stationnement sur le lieu de travail ou d'études
    "P18A": pl.UInt8,  # Stationnement du vélo sur le lieu de travail / études
    "P19": pl.UInt8,  # Fréquence de déplacement à pied
    "P20": pl.UInt8,  # Fréquence d’utilisation d'un vélo
    "P21": pl.UInt8,  # Fréquence d’utilisation d'un deux-roues motorisé
    "P22": pl.UInt8,  # Fréquence d’utilisation de la VP en tant que conducteur
    "P23": pl.UInt8,  # Fréquence d’utilisation de la VP en tant que passager
    "P24": pl.UInt8,  # Fréquence d’utilisation du réseau urbain
    "P25": pl.UInt8,  # Situation la veille du jour d’enquête
    "P26": pl.UInt8,  # Travail la veille
    "COE1": pl.Float64,  # Coefficient de redressement -Toutes Personnes
    "COEP": pl.Float64,  # Coefficient de redressement - Personnes Enquêtées
}

REFERENCE_PERSON_LINK_MAP = {
    1: "reference_person",  # Personne de référence
    2: "spouse",  # Conjoint
    3: "child",  # Enfant
    4: "roommate_or_tenant",  # Colocataire, locataire ou sous-locataire
    5: "other:relative",  # Autre (avec lien de parenté)
    6: "other:non_relative",  # Autre (sans lien de parenté)
    7: "other:non_relative",  # Autre Non précisé
}

200 / 2600 / 2490 / 2809
DRIVING_LICENSE_MAP = {
    1: "yes",
    2: "no",
    3: "in_progress",  # Conduite accompagnée et leçons de conduite
}

EDUCATION_LEVEL_MAP = {
    0: None,  # En cours de scolarité
    1: "primary",  # Primaire
    2: "secondary:no_bac",  # Secondaire (de la 6e à la 3e, CAP)
    3: "secondary:no_bac",  # Secondaire (de la seconde à la terminale, BEP), non titulaire du bac
    4: "secondary:bac",  # Secondaire, titulaire du bac
    5: "higher:at_most_bac+2",  # Supérieur jusqu’à bac + 2
    6: "higher:at_least_bac+3",  # Supérieur, bac + 3 et plus
    # Apprentissage is usually something like CAP so we put secondary:no_bac
    7: "secondary:no_bac",  # Apprentissage (école primaire ou secondaire uniquement)
    # Apprentissage (études supérieurs) should rarely be higher than BAC+2
    8: "higher:at_most_bac+2",  # Apprentissage (études supérieures)
    9: "no_studies_or_no_diploma",  # Pas d’études
    # For the two modalities below we have to make an assumption.
    93: "secondary:no_bac",  # Secondaire (sans distinction titulaire du bac ou non)
    97: "secondary:no_bac",  #  Apprentissage (sans distinction)
    90: None,  # autre (egt)
}

DETAILED_EDUCATION_LEVEL_MAP = {
    0: None,  # En cours de scolarité
    1: "primary:unspecified",  # Primaire
    # CAP should actually be in the other category but given that EMC2 are the only one to do that
    # there is no appropriate category.
    2: "secondary:no_bac:college",  # Secondaire (de la 6e à la 3e, CAP)
    3: "secondary:no_bac:CAP/BEP",  # Secondaire (de la seconde à la terminale, BEP), non titulaire du bac
    4: "secondary:bac:unspecified",  # Secondaire, titulaire du bac
    5: "higher:at_most_bac+2:unspecified",  # Supérieur jusqu’à bac + 2
    6: "higher:at_least_bac+3:unspecified",  # Supérieur, bac + 3 et plus
    7: "secondary:no_bac:CAP/BEP",  # Apprentissage (école primaire ou secondaire uniquement)
    8: "higher:at_most_bac+2:unspecified",  # Apprentissage (études supérieures)
    9: "no_studies",  # Pas d’études
    93: None,  # Secondaire (sans distinction titulaire du bac ou non)
    97: None,  #  Apprentissage (sans distinction)
    90: None,  # autre (egt)
}

DETAILED_PROFESSIONAL_OCCUPATION_MAP = {
    1: "worker:full_time",  # Travail à plein temps.
    2: "worker:part_time",  # Travail à temps partiel.
    3: "student:apprenticeship",  # Formation en alternance (apprentissage, professionnalisation), stage.
    4: "student:higher",  # Étudiant.
    5: "student:primary_or_secondary",  # Scolaire jusqu'au bac.
    6: "other:unemployed",  # Chômeur, recherche un emploi.
    7: "other:retired",  # Retraité.
    8: "other:homemaker",  # Reste au foyer.
    9: "other:unspecified",  # Autre.
}

SECONDARY_PROFESSIONAL_OCCUPATION_MAP = {
    0: None,  # Non concerné
    1: "work",  # Travail
    2: "education",  # Etudes
}

PCS_GROUP_CODE_MAP = {
    0: None,  # Non réponse
    1: 1,  # Agriculteurs exploitants
    2: 2,  # Artisans, commerçants et chefs d'entreprise
    3: 3,  # Cadres et professions intellectuelles supérieures
    4: 4,  # Professions Intermédiaires
    5: 5,  # Employés
    6: 6,  # Ouvriers
    7: None,  # Élèves, étudiants
    8: 8,  # Chômeurs n'ayant jamais travaillé
    9: 8,  # Autres inactifs n'ayant jamais travaillé
}

# NOTE. Some details are lost here because it is unclear what "Secondaires, titulaires du Bac" means.
# I think it's fine because we still keep the main information.
STUDENT_GROUP_MAP = {
    83: "primaire",  # Écoliers (primaire)
    84: "collège",  # Secondaires jusqu'en 3ème
    85: "lycée",  # Secondaires, de la seconde à la terminale
    86: None,  # Secondaires, titulaires du Bac  Special case, see below.
    90: "lycée",  # Secondaires, de la seconde à la terminale (Sans précision des titulaires du Bac ou non) egt
    87: "supérieur",  # Supérieurs (Bac+2)
    80: "supérieur",  # Sans précision secondaires titulaires du Bac + supérieurs (Bac+2)
    88: "supérieur",  # Supérieurs (Bac+3 et plus)
    89: "lycée",  # Apprentis  # NOTE. I assume here that this is not used for "alternant"
}

PUBLIC_TRANSIT_SUBSCRIPTION_MAP = {
    1: "yes:free",  # Oui, gratuit
    2: "yes:paid:with_employer_contribution",  # Oui, payant avec prise en charge partielle par l'employeur
    3: "yes:paid:without_employer_contribution",  # Oui, payant sans prise en charge partielle par l'employeur
    4: "no",  # Non
    5: "yes:paid",  # Oui, payant (sans information sur la prise en charge)
    6: "yes:unspecified",  # Oui, mais sans précision
}

HAS_CAR_TO_COMMUTE_MAP = {
    1: "yes:full_commute",  # Oui et je l’utilise jusqu'à mon lieu de travail ou d'études
    2: "yes:partial_commute",  # Oui mais je ne l’utilise que sur une partie du déplacement
    3: "yes:not_used",  # Oui, mais je ne l’utilise pas
    4: "no",  # Non
    5: "yes:partial_or_not_used",  # Oui, mais je ne l'utilise qu'en partie ou pas du tout (2+3 sans distinction)
    6: "yes:full_or_partial",  # Oui et je l’utilise pour tout ou partie du déplacement (1+2 sans distinction)
}

TELEWORK_MAP = {
    1: "no",  # Non, jamais
    2: "yes:weekly",  #  Oui, un ou plusieurs jours par semaine
    3: "yes:monthly",  # Oui, plusieurs jours par mois
    4: "yes:occasionally",  # Oui, occasionnellement
}

WORK_STUDY_CAR_PARKING_MAP = {
    1: "no",  # Non
    2: "yes:reserved",  # Oui , car j’ai (ou pourrai avoir) une place réservée
    3: "yes:many_spots",  # Oui, offre importante à proximité
    4: "yes:compatible_schedule",  # Oui, compte tenu de mes horaires
    5: "dont_know",  # Ne sait pas (EMC2 only)
}

WORK_STUDY_BICYCLE_PARKING_MAP = {
    1: "yes:on_site:sheltered",  # Oui, dans l'enceinte du lieu et abrité
    2: "yes:on_site:unsheltered",  # Oui, dans l'enceinte du lieu mais non abrité
    3: "yes:nearby:sheltered",  # Oui, à proximité du lieu et abrité
    4: "yes:nearby:unsheltered",  # Oui, à proximité du lieu mais non abrité
    5: "no",  # Non
    6: "yes:on_site",  # Oui, dans l'enceinte du lieu sans précision
    7: "yes:nearby",  # Oui, à proximité du lieu sans précision
    9: None,  # NR-Refus
}

TRAVELED_DAY_BEFORE_MAP = {
    1: "yes",  # Oui
    2: "no",  # Non
    3: "away",  # Absent (vieille enquête)
    4: None,  # déplacements non relevés
    5: "away",  # absent - longue durée-
    9: None,
}

WORKED_DAY_BEFORE_MAP = {
    0: None,  # Note. Used in some surveys but undefined.
    1: "yes:outside",  # Oui, hors du domicile.
    2: "yes:home:usual",  # Oui mais à domicile (travail toujours au domicile).
    3: "yes:home:telework",  # Oui mais à domicile – télétravail.
    4: "yes:home:other",  # Oui mais à domicile - autre
    5: "no:weekday",  # Non, ne travaille jamais ce jour-là.
    6: "no:reason",  # Non en raison de congés, grève ou maladie.
    7: "yes:unspecified",  # oui (sans précision)
    8: "no:unspecified",  # non (sans précision)
    9: "no:unspecified",  # Used in some surveys
}


def scan_persons_impl(source: str | io.BytesIO):
    return pl.scan_csv(source, separator=";", schema_overrides=SCHEMA, null_values=["a", "aa"])


class PersonsReader:
    def scan_persons(self):
        lfs_iter = map(scan_persons_impl, self.persons_filenames())
        lf = pl.concat(lfs_iter, how="vertical")
        lf = lf.sort(self.get_person_index_cols())
        columns = lf.collect_schema().names()
        if "P13B" not in columns:
            # In the old Cerema surveys (EMD, EDGT, EDVM), the P13B column does not exist.
            lf = lf.with_columns(P13B=pl.lit(None, dtype=pl.UInt8))
        if "P17" not in columns:
            # In the EMC2 surveys, the P17 column does not exist.
            lf = lf.with_columns(P17=pl.lit(None, dtype=pl.UInt8))
        if "ANNEE" not in columns:
            # In the EMC2 surveys, the ANNEE column is now AN.
            lf = lf.rename({"AN": "ANNEE"})
        return lf

    def standardize_persons(self):
        lf = self.scan_persons()
        # Add household_id.
        lf = lf.with_columns(
            original_household_id=pl.struct(**self.get_household_index_cols_from_persons())
        ).join(
            self.households.select("original_household_id", "household_id"),
            on="original_household_id",
            how="left",
            coalesce=True,
        )
        lf = lf.rename({"P4": "age", "COE1": "sample_weight_all", "COEP": "sample_weight_surveyed"})
        lf = fix_dates(lf)
        lf = lf.with_columns(
            original_person_id=pl.struct(self.get_person_index_cols()),
            trip_date=pl.date(year="ANNEE", month="month", day="day"),
            # The `fill_null` is required here because in some cases, a null value is used instead
            # of 0.
            is_surveyed=(pl.col("PENQ") == 1).fill_null(False),
            woman=pl.col("P2") == 2,
            reference_person_link=pl.col("P3").replace_strict(REFERENCE_PERSON_LINK_MAP),
            has_driving_license=pl.col("P7").replace_strict(DRIVING_LICENSE_MAP),
            education_level=pl.col("P8").replace_strict(EDUCATION_LEVEL_MAP),
            detailed_education_level=pl.col("P8").replace_strict(DETAILED_EDUCATION_LEVEL_MAP),
            detailed_professional_occupation=pl.col("P9").replace_strict(
                DETAILED_PROFESSIONAL_OCCUPATION_MAP
            ),
            secondary_professional_occupation=pl.col("P10").replace_strict(
                SECONDARY_PROFESSIONAL_OCCUPATION_MAP
            ),
            pcs_group_code=pl.col("PCSC").replace_strict(PCS_GROUP_CODE_MAP),
            pcs_category_code2003=pl.when(pl.col("PCSD").is_between(1, 69)).then("PCSD"),
            # Special case for PCSD="86" (Secondaires, titulaires du Bac).
            student_group=pl.when(PCSD=86)
            .then(
                # If P9 is "Scolaire jusqu'au bac", assume that 86 means "lycée".
                pl.when(P9=5)
                .then(pl.lit("lycée"))
                # If P9 is "Étudiant" or "Alternance", assume that 86 means "supérieur".
                .when(pl.col("P9").is_in((3, 4)))
                .then(pl.lit("supérieur"))
                .otherwise(pl.lit(None))
            )
            .otherwise(pl.col("PCSD").replace_strict(STUDENT_GROUP_MAP, default=None)),
            has_public_transit_subscription=pl.col("P12") != 4,
            public_transit_subscription=pl.col("P12").replace_strict(
                PUBLIC_TRANSIT_SUBSCRIPTION_MAP
            ),
            telework=pl.col("P13B").replace_strict(TELEWORK_MAP),
            traveled_during_surveyed_day=pl.col("P25").replace_strict(TRAVELED_DAY_BEFORE_MAP),
            worked_during_surveyed_day=pl.col("P26").replace_strict(WORKED_DAY_BEFORE_MAP),
            is_student=pl.col("P9").is_in((3, 4, 5)),
            is_not_student=pl.col("P8") != 0,
            insee=pl.col("GP5").replace(["aaaaa", "999999", "888888"], None),
            # Column P17 is just an improved version of column P18.
            work_study_parking=pl.col("P17").fill_null(pl.col("P18")),
        )
        lf = lf.with_columns(
            work_only_at_home=pl.when("is_not_student").then(pl.col("P14") == 1),
            study_only_at_home=pl.when("is_student").then(pl.col("P14") == 1),
            work_detailed_zone=pl.when("is_not_student").then("P15"),
            study_detailed_zone=pl.when("is_student").then("P15"),
            work_draw_zone=pl.when("is_not_student").then("STW"),
            study_draw_zone=pl.when("is_student").then("STW"),
            work_insee=pl.when("is_not_student").then("insee"),
            study_insee=pl.when("is_student").then("insee"),
            work_commute_euclidean_distance_km=pl.when("is_not_student").then(pl.col("DP15") / 1e3),
            study_commute_euclidean_distance_km=pl.when("is_student").then(pl.col("DP15") / 1e3),
            has_car_for_work_commute=pl.when("is_not_student").then(
                pl.col("P16").replace_strict(HAS_CAR_TO_COMMUTE_MAP)
            ),
            has_car_for_study_commute=pl.when("is_student").then(
                pl.col("P16").replace_strict(HAS_CAR_TO_COMMUTE_MAP)
            ),
            work_car_parking=pl.when("is_not_student").then(
                pl.col("work_study_parking").replace_strict(WORK_STUDY_CAR_PARKING_MAP)
            ),
            study_car_parking=pl.when("is_student").then(
                pl.col("work_study_parking").replace_strict(WORK_STUDY_CAR_PARKING_MAP)
            ),
            work_bicycle_parking=pl.when("is_not_student").then(
                pl.col("P18A").replace_strict(WORK_STUDY_BICYCLE_PARKING_MAP)
            ),
            study_bicycle_parking=pl.when("is_student").then(
                pl.col("P18A").replace_strict(WORK_STUDY_BICYCLE_PARKING_MAP)
            ),
        )
        lf = fix_work_study_location(lf, self.households)
        lf = extra_fixes(lf)
        lf = lf.sort("original_person_id")
        self.persons = clean(
            lf,
            special_locations=self.special_locations_coords,
            detailed_zones=self.detailed_zones_coords,
            extra_cols=["trip_date"],
        )
        # When the INSEE code ends with "000" or "999" it means "rest of the département".
        # We drop these values because they do not add any additional information compared to `_dep`
        # columns.
        # This is done after the automatic cleaning so that the département is correctly read.
        self.persons = self.persons.with_columns(
            work_insee=pl.when(
                pl.col("work_insee").str.ends_with("000")
                | pl.col("work_insee").str.ends_with("999")
            )
            .then(None)
            .otherwise("work_insee"),
            study_insee=pl.when(
                pl.col("study_insee").str.ends_with("000")
                | pl.col("study_insee").str.ends_with("999")
            )
            .then(None)
            .otherwise("study_insee"),
        )


# For Arras 2014, the "MOIS" column is always 14 (for 2014) and the "DATE" column
# corresponds to the month (January or February). The exact date is unknown. We set to a random date
# in January or February so that at least the weekday matches properly (given that having a date
# that is a bit off is probably better than having a NULL date).
ARRAS_JANUARY_WEEKDAY_MAP = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}
ARRAS_FEBRUARY_WEEKDAY_MAP = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7}


def fix_dates(lf: pl.LazyFrame):
    # Arras 2014 case.
    lf = lf.with_columns(
        month=pl.when(ANNEE=2014, MOIS=14).then("DATE").otherwise("MOIS"),
        day=pl.when(ANNEE=2014, MOIS=14, JOUR=1)
        .then(pl.col("JOUR").replace_strict(ARRAS_JANUARY_WEEKDAY_MAP))
        .when(ANNEE=2014, MOIS=14, JOUR=2)
        .then(pl.col("JOUR").replace_strict(ARRAS_FEBRUARY_WEEKDAY_MAP))
        .otherwise("DATE"),
    )
    # In some cases (e.g., Valenciennes 2011), "MOIS" and "DATE" columns seem to be inverted.
    lf = lf.with_columns(
        month=pl.when(pl.col("month") > 12).then("day").otherwise("month"),
        day=pl.when(pl.col("month") > 12).then("month").otherwise("day"),
    )
    # For Valenciennes 2011, there are some dates equal to 31st April (which does not exist).
    # My guess is that they meant 31st March.
    lf = lf.with_columns(
        month=pl.when(ANNEE=2011, MOIS=4, DATE=31).then(3).otherwise("month"),
    )
    return lf


def fix_work_study_location(lf: pl.LazyFrame, households: pl.LazyFrame):
    # In many cases, the work location is set to the home location when `work_only_at_home` is
    # true, instead they should be set to NULL.
    zone_cols = ("detailed_zone", "draw_zone", "insee")
    lf = lf.join(
        households.select("household_id", *(f"home_{col}" for col in zone_cols)),
        on="household_id",
        how="left",
    )
    lf = lf.with_columns(
        pl.when("work_only_at_home", pl.col(f"home_{col}") == pl.col(f"work_{col}"))
        .then(None)
        .otherwise(f"work_{col}")
        .alias(f"work_{col}")
        for col in zone_cols
    )
    # Same thing for study location.
    lf = lf.with_columns(
        pl.when("study_only_at_home", pl.col(f"home_{col}") == pl.col(f"study_{col}"))
        .then(None)
        .otherwise(f"study_{col}")
        .alias(f"study_{col}")
        for col in zone_cols
    )
    # Similarly, work and study commute distance must be set to 0 when working / studying only at
    # home (they can be set to a positive value depending on the home insee area size).
    lf = lf.with_columns(
        work_commute_euclidean_distance_km=pl.when("work_only_at_home")
        .then(0.0)
        .otherwise("work_commute_euclidean_distance_km"),
        study_commute_euclidean_distance_km=pl.when("study_only_at_home")
        .then(0.0)
        .otherwise("study_commute_euclidean_distance_km"),
    )
    # For external work / study location, the detailed zone id is sometimes set to "8" + INSEE or
    # "9" + INSEE. In this case, keeping the detailed zone id does not add any information so we set
    # it to NULL.
    lf = lf.with_columns(
        work_detailed_zone=pl.when("8" + pl.col("work_insee") == pl.col("work_detailed_zone"))
        .then(None)
        .when("9" + pl.col("work_insee") == pl.col("work_detailed_zone"))
        .then(None)
        .otherwise("work_detailed_zone"),
        study_detailed_zone=pl.when("8" + pl.col("study_insee") == pl.col("study_detailed_zone"))
        .then(None)
        .when("9" + pl.col("study_insee") == pl.col("study_detailed_zone"))
        .then(None)
        .otherwise("study_detailed_zone"),
    )
    # Values 99000, 99999, 99095, 99300 do not represent any known INSEE / country.
    lf = lf.with_columns(
        work_insee=pl.col("work_insee").replace(["99000", "99999", "99095", "99300"], None),
        study_insee=pl.col("study_insee").replace(["99000", "99999", "99095", "99300"], None),
    )
    return lf


def extra_fixes(lf: pl.LazyFrame):
    # For Nice 2009 and Toulouse 2013, some persons have `student_group` = "supérieur" but their
    # `detailed_professional_occupation` is "student:primary_or_secondary".
    # If they are over 18, the `detailed_professional_occupation` is switched to
    # "student:higher".
    # If they are below 18, the `student_group` is switched to "lycée".
    mask = pl.col("student_group").eq("supérieur") & pl.col("detailed_professional_occupation").eq(
        "student:primary_or_secondary"
    )
    lf = lf.with_columns(
        detailed_professional_occupation=pl.when(pl.col("age").ge(18) & mask)
        .then(pl.lit("student:higher"))
        .otherwise("detailed_professional_occupation"),
        student_group=pl.when(pl.col("age").lt(18) & mask)
        .then(pl.lit("lycée"))
        .otherwise("student_group"),
    )
    # For Douai 2015 and Strasbourg 2009, some persons have `student_group` = "primaire" but their
    # `detailed_professional_occupation` is not "student:primary_or_secondary".
    # If they are over 12, the `student_group` is switched to NULL.
    # If they are below 12, the `detailed_professional_occupation` is switched to
    # "student:primary_or_secondary".
    mask = pl.col("student_group").eq("primaire") & pl.col("detailed_professional_occupation").ne(
        "student:primary_or_secondary"
    )
    lf = lf.with_columns(
        detailed_professional_occupation=pl.when(pl.col("age").lt(12) & mask)
        .then(pl.lit("student:primary_or_secondary"))
        .otherwise("detailed_professional_occupation"),
        student_group=pl.when(pl.col("age").ge(12) & mask).then(None).otherwise("student_group"),
    )
    lf = lf.with_columns(
        # `secondary_professional_occupation` cannot be "education" for students.
        secondary_professional_occupation=pl.when(
            pl.col("detailed_professional_occupation").str.starts_with("student"),
            pl.col("secondary_professional_occupation").eq("education"),
        )
        .then(None)
        # `secondary_professional_occupation` cannot be "work" for workers.
        .when(
            pl.col("detailed_professional_occupation").str.starts_with("worker"),
            pl.col("secondary_professional_occupation").eq("work"),
        )
        .then(None)
        .otherwise("secondary_professional_occupation")
    )
    lf = lf.with_columns(
        # The `traveled_during_surveyed_day` variable must be set to null for non-surveyed
        # persons.
        traveled_during_surveyed_day=pl.when("is_surveyed").then("traveled_during_surveyed_day"),
        # Same think for `worked_during_surveyed_day`.
        worked_during_surveyed_day=pl.when("is_surveyed").then("worked_during_surveyed_day"),
        # The `sample_weight_surveyed` variable must be set to null for non-surveyed
        # persons.
        sample_weight_surveyed=pl.when("is_surveyed").then("sample_weight_surveyed"),
    )
    # For Clermont-Ferrand 2012, one person is "other:relative" when it should be "reference_person"
    # (there are only 2 persons in the household: "other:relative" and "spouse").
    lf = lf.with_columns(
        reference_person_link=pl.when(
            pl.col("reference_person_link").eq("other:non_relative")
            & pl.len().over("household_id").eq(2)
            & pl.col("reference_person_link").eq("spouse").any().over("household_id")
        )
        .then(pl.lit("reference_person"))
        .otherwise("reference_person_link")
    )
    return lf
