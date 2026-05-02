"""Immunization catalog with age-appropriate filtering.

CVX codes are the CDC Vaccine Administered code set, the standard for US
immunization records. Each ImmunizationDef includes the minimum and maximum
patient age (in years) for which the vaccine is appropriate.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImmunizationDef:
    cvx_code: str
    display: str
    min_age: int = 0
    max_age: int = 999  # 999 = no upper limit
    # Probability that an age-eligible patient has received this vaccine
    prevalence: float = 0.85


IMMUNIZATIONS: list[ImmunizationDef] = [
    ImmunizationDef("08",  "Hepatitis B vaccine",                               min_age=0,  max_age=999, prevalence=0.90),
    ImmunizationDef("03",  "MMR (measles, mumps, rubella) vaccine",             min_age=1,  max_age=999, prevalence=0.92),
    ImmunizationDef("21",  "Varicella vaccine",                                 min_age=1,  max_age=999, prevalence=0.88),
    ImmunizationDef("20",  "DTaP (diphtheria, tetanus, acellular pertussis)",   min_age=0,  max_age=7,   prevalence=0.93),
    ImmunizationDef("113", "Tetanus and diphtheria toxoids (Td) booster",       min_age=7,  max_age=999, prevalence=0.75),
    ImmunizationDef("10",  "Inactivated poliovirus vaccine (IPV)",              min_age=0,  max_age=999, prevalence=0.91),
    ImmunizationDef("33",  "Pneumococcal polysaccharide vaccine (PPSV23)",      min_age=65, max_age=999, prevalence=0.70),
    ImmunizationDef("133", "Pneumococcal conjugate vaccine 13-valent (PCV13)", min_age=0,  max_age=5,   prevalence=0.88),
    ImmunizationDef("141", "Influenza vaccine (seasonal, inactivated)",         min_age=0,  max_age=999, prevalence=0.60),
    ImmunizationDef("62",  "HPV vaccine",                                       min_age=9,  max_age=45,  prevalence=0.55),
    ImmunizationDef("83",  "Hepatitis A vaccine",                               min_age=1,  max_age=999, prevalence=0.72),
    ImmunizationDef("140", "Influenza vaccine for intranasal use (LAIV)",       min_age=2,  max_age=49,  prevalence=0.15),
    ImmunizationDef("217", "COVID-19 mRNA vaccine (Moderna)",                   min_age=6,  max_age=999, prevalence=0.65),
    ImmunizationDef("218", "COVID-19 mRNA vaccine (Pfizer-BioNTech)",           min_age=5,  max_age=999, prevalence=0.65),
    ImmunizationDef("187", "Zoster (shingles) recombinant vaccine (RZV)",       min_age=50, max_age=999, prevalence=0.45),
    ImmunizationDef("115", "Meningococcal conjugate vaccine (MCV4)",            min_age=11, max_age=23,  prevalence=0.80),
    ImmunizationDef("136", "Meningococcal B vaccine",                           min_age=10, max_age=25,  prevalence=0.35),
    ImmunizationDef("122", "Rotavirus vaccine (pentavalent)",                   min_age=0,  max_age=1,   prevalence=0.85),
]
