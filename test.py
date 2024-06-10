import unittest
from main import ResultData, SatelliteData, calculateResultData

class TestDataTest(unittest.TestCase):
    def runTest(self):
        test_data = SatelliteData(
            sv_nr=1,
            year=2023,
            month=4,
            day=4,
            hour=1,
            minute=15,
            toc=177299.999803551,
            week=2256,
            a0=0.0,
            a1=1.0,
            a2=0.0,
            Crs=64.65625,
            deln=3.68408202823e-09,
            M0=-3.12525956676,
            Cuc =3.14973294735e-06,
            e=0.0126234182389,
            Cus=1.15595757961e-05,
            a=26560136.90362,
            toe =172800,
            Cic=6.14672899246e-08,
            om0=-3.01249823912,
            Cis=-1.99303030968e-07,
            i0=0.990046368914,
            Crc=169.5625,
            om=0.944285937368,
            omdot=-7.41995192792e-09,
            Idot=2.67153985179e-10
        )

        correct_result = ResultData(
            czas_obliczen = 4499.999803551,
            anomalia_srednia = -2.4688922918137,
            anomalia_mimosrodowa = -2.4766808114941,
            sin = -0.61087203109961,
            cos = -0.79172934871724,
            nu = -2.484431104294,
            anomalia_prawdziwa = -2.484431104294,
            F = -1.540145166926,
            u_poprawione = -1.5401490189276,
            r_poprawione = 26823819.172984,
            i_poprawione = 0.99004752196514,
            Xp = 821949.15995402,
            Yp = -26811222.922564,
            rektascenzja_wezla_poprawiona = -15.941451769676,
            X=2603843.27,
            Y=14501004.80,
            Z=-22415577.95
        )

        c = calculateResultData(test_data)
        for field in correct_result.__dataclass_fields__:
            calculated = getattr(c, field)
            expected = getattr(correct_result, field)
            # round calculated to decimal places of expected
            calculated = round(calculated, len(str(expected).split(".")[1]))
            if calculated != expected:
                print(f"{field}: {calculated} != {expected}")
            self.assertTrue(abs(calculated - expected) < 0.0001* abs(expected), f"Field {field} is not equal")


if __name__ == '__main__':
    unittest.main()