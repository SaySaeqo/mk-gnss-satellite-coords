from dataclasses import dataclass
from math import sin, cos, atan2
import urllib.request
import gzip


class Constants:
    gm = 3.986005e14
    omega_e = 7.2921151467e-5

@dataclass
class SatelliteData:
    sv_nr: int
    year: int
    month: int
    day: int
    hour: int
    minute: int
    toc: float
    week: int
    a0: float
    a1: float
    a2: float
    Crs: float
    deln: float
    M0: float
    Cuc: float
    e: float
    Cus: float
    a: float
    toe: float
    Cic: float
    om0: float
    Cis: float
    i0: float
    Crc: float
    om: float
    omdot: float
    Idot: float

@dataclass
class ResultData:
    czas_obliczen: float
    anomalia_srednia: float
    anomalia_mimosrodowa: float
    sin: float
    cos: float
    nu: float
    anomalia_prawdziwa: float
    F: float
    u_poprawione: float
    r_poprawione: float
    i_poprawione: float
    Xp: float
    Yp: float
    rektascenzja_wezla_poprawiona: float
    X: float
    Y: float
    Z: float

    def __repr__(self) -> str:
        # return all fields in next line
        fields = [f"{field}: {getattr(self, field)}" for field in self.__dataclass_fields__]
        return "\n".join(fields)



def calculateResultData(data: SatelliteData) -> ResultData:

    # wyznaczanie czasu obliczeń
    tsv = data.toc + 60
    deltsv = data.a0 + data.a1 * (tsv - data.toc) + data.a2 * (tsv - data.toc) ** 2
    t = tsv - deltsv
    tk = t - data.toe
    
    # wyznaczanie anomali średniej
    n0 = (Constants.gm / data.a ** 3) ** 0.5
    n = n0 + data.deln
    Mk = data.M0 + n * tk

    # wyznaczanie anomali mimośrodowej
    Ek = Mk
    ITERATIONS = 10
    for i in range(ITERATIONS):
        Ek = Mk + data.e * sin(Ek)

    # wyznaczanie anomali prawdziwej
    cos_vk = (cos(Ek) - data.e) / (1 - data.e * cos(Ek))
    sin_vk = (1 - data.e ** 2) ** 0.5 * sin(Ek) / (1 - data.e * cos(Ek))

    # wyznaczanie argumentu szerokości geocentrycznej
    vk = atan2(sin_vk, cos_vk)
    Fk = vk + data.om
    duk = data.Cus * sin(2 * Fk) + data.Cuc * cos(2 * Fk)
    drk = data.Crs * sin(2 * Fk) + data.Crc * cos(2 * Fk)
    dik = data.Cis * sin(2 * Fk) + data.Cic * cos(2 * Fk)
    uk = Fk + duk
    rk = data.a * (1 - data.e * cos(Ek)) + drk
    ik = data.i0 + dik + data.Idot * tk

    # wyznaczanie współrzędnych satelity w układzie orbitalnym
    XPk = rk * cos(uk)
    YPk = rk * sin(uk)

    # wyznaczanie korekcji RAAN
    omk = data.om0 + (data.omdot - Constants.omega_e) * tk - Constants.omega_e * data.toe

    # wyznaczanie współrzędnych satelity w układzie ziemskim
    Xk = XPk * cos(omk) - YPk * cos(ik) * sin(omk)
    Yk = XPk * sin(omk) + YPk * cos(ik) * cos(omk)
    Zk = YPk * sin(ik)



    return ResultData(
        czas_obliczen = tk,
        anomalia_srednia = Mk,
        anomalia_mimosrodowa = Ek,
        sin = sin_vk,
        cos = cos_vk,
        nu = vk,
        anomalia_prawdziwa = vk,
        F = Fk,
        u_poprawione = uk,
        r_poprawione = rk,
        i_poprawione = ik,
        Xp = XPk,
        Yp = YPk,
        rektascenzja_wezla_poprawiona = omk,
        X = Xk,
        Y = Yk,
        Z = Zk
    )


if __name__ == '__main__':
    # download data from brdc gps broadcast orbits (BRDC)
    # url = "https://cddis.nasa.gov/archive/gnss/data/daily/2021/brdc/brdc0150.21g.gz"
    # response = urllib.request.urlretrieve(url, "brdc0150.21g.gz")
    # with open("brdc0150.21g.gz", "rb") as f:
    #     unzipped = gzip.decompress(f.read())
    #     print(unzipped)

    with open("./brdc0240.21n", "r") as f:
        lines = f.readlines()
        after_header = False
        i = 0
        SHORT_DATA_LEN = 2
        LONG_DATA_LEN = 19
        PADDING = 3
        START_POSITIONS = [
            0,
            SHORT_DATA_LEN,
            2*(SHORT_DATA_LEN + 1),
            3*(SHORT_DATA_LEN + 1),
            4*(SHORT_DATA_LEN + 1),
            5*(SHORT_DATA_LEN + 1),
            6*(SHORT_DATA_LEN + 1),
            PADDING + LONG_DATA_LEN,
            PADDING + 2*LONG_DATA_LEN,
            PADDING + 3*LONG_DATA_LEN,
            79
        ]
        START_POSITIONS2 = [
            0,
            PADDING + LONG_DATA_LEN,
            PADDING + 2*LONG_DATA_LEN,
            PADDING + 3*LONG_DATA_LEN,
            79
        ]

        SLICES = [ slice(x0,x1) for x0, x1 in zip(START_POSITIONS, START_POSITIONS[1:]) ]
        SLICES2 = [ slice(x0,x1) for x0, x1 in zip(START_POSITIONS2, START_POSITIONS2[1:]) ]
        while i < len(lines):
            if lines[i].find("END OF HEADER") != -1:
                after_header = True
                i += 1
                continue
            elif not after_header:
                i += 1
            
            if after_header:
                data = SatelliteData(
                    sv_nr=int(lines[i][SLICES[0]].strip()),
                    year=int(lines[i][SLICES[1]].strip().replace("D", "e")),
                    month=int(lines[i][SLICES[2]].strip().replace("D", "e")),
                    day=int(lines[i][SLICES[3]].strip().replace("D", "e")),
                    hour=int(lines[i][SLICES[4]].strip().replace("D", "e")),
                    minute=int(lines[i][SLICES[5]].strip().replace("D", "e")),
                    toc=float(lines[i][SLICES[6]].strip().replace("D", "e")),
                    a0=float(lines[i][SLICES[7]].strip().replace("D", "e")),
                    a1=float(lines[i][SLICES[8]].strip().replace("D", "e")),
                    a2=float(lines[i][SLICES[9]].strip().replace("D", "e")),
                    Crs=float(lines[i+1][SLICES2[1]].strip().replace("D", "e")),
                    deln=float(lines[i+1][SLICES2[2]].strip().replace("D", "e")),
                    M0=float(lines[i+1][SLICES2[3]].strip().replace("D", "e")),
                    Cuc=float(lines[i+2][SLICES2[0]].strip().replace("D", "e")),
                    e=float(lines[i+2][SLICES2[1]].strip().replace("D", "e")),
                    Cus=float(lines[i+2][SLICES2[2]].strip().replace("D", "e")),
                    a=float(lines[i+2][SLICES2[3]].strip().replace("D", "e"))**2,
                    toe=float(lines[i+3][SLICES2[0]].strip().replace("D", "e")),
                    Cic=float(lines[i+3][SLICES2[1]].strip().replace("D", "e")),
                    om0=float(lines[i+3][SLICES2[2]].strip().replace("D", "e")),
                    Cis=float(lines[i+3][SLICES2[3]].strip().replace("D", "e")),
                    i0=float(lines[i+4][SLICES2[0]].strip().replace("D", "e")),
                    Crc=float(lines[i+4][SLICES2[1]].strip().replace("D", "e")),
                    om=float(lines[i+4][SLICES2[2]].strip().replace("D", "e")),
                    omdot=float(lines[i+4][SLICES2[3]].strip().replace("D", "e")),
                    Idot=float(lines[i+5][SLICES2[0]].strip().replace("D", "e")),
                    week=int(float(lines[i+5][SLICES2[2]].strip().replace("D", "e")))
                )
                i += 8
                result = calculateResultData(data)
                print(result)
                continue_prompt = input("Continue? (y/n): ")
                if continue_prompt.lower() != "y":
                    break