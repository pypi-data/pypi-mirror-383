import xraylib
import numpy as np
import pytest

from ewokstomo.tasks import energycalculation as ec

try:
    from ewokscore.missing_data import MissingData
except Exception:  # pragma: no cover - optional dependency in tests
    MissingData = None


def test_resolve_mu_density_element_auto_density():
    energies = np.array([10.0, 20.0], dtype=float)

    mu_over_rho, rho = ec._resolve_mu_density("Al", "?", energies)

    Z = xraylib.SymbolToAtomicNumber("Al")
    expected_mu = np.array([xraylib.CS_Total(Z, energy) for energy in energies])
    expected_rho = xraylib.ElementDensity(Z)

    assert rho == pytest.approx(expected_rho)
    np.testing.assert_allclose(mu_over_rho, expected_mu)


def test_resolve_mu_density_compound_uses_alias():
    energies = np.array([1.0, 2.0, 4.0], dtype=float)

    mu_over_rho, rho = ec._resolve_mu_density(" kapton ", None, energies)

    cname = ec._canonical_compound_name("kapton") or "Kapton Polyimide Film"
    data = xraylib.GetCompoundDataNISTByName(cname)
    Zs = data["Elements"]
    weights = data["massFractions"]
    expected = np.zeros_like(energies, dtype=float)
    for Z, wf in zip(Zs, weights):
        expected += wf * np.array([xraylib.CS_Total(int(Z), e) for e in energies])

    assert rho == pytest.approx(data["density"])
    np.testing.assert_allclose(mu_over_rho, expected)


def test_apply_attenuators_respects_order_duplicates():
    energy = np.array([5000.0, 12000.0])
    spectral_power = np.array([10.0, 20.0])
    flux = np.array([5.0, 5.0])
    rho_al = xraylib.ElementDensity(xraylib.SymbolToAtomicNumber("Al"))

    task = ec.ApplyAttenuators(
        inputs={
            "energy_eV": energy,
            "spectral_power": spectral_power,
            "flux": flux,
            "attenuators": {
                "first": {
                    "material": "Al",
                    "thickness_mm": 1.0,
                    "density_g_cm3": rho_al,
                },
            },
            "order": ["first", "first"],
        }
    )
    task.run()

    single = ec._transmission("Al", 1.0, rho_al, energy)
    combined = single * single
    np.testing.assert_allclose(task.outputs.transmission, combined)
    np.testing.assert_allclose(
        task.outputs.attenuated_spectral_power,
        spectral_power * combined,
    )
    np.testing.assert_allclose(
        task.outputs.attenuated_flux,
        flux * combined,
    )


def test_apply_attenuators_without_flux():
    energy = np.array([8000.0, 30000.0])
    spectral_power = np.array([1.0, 2.0])
    rho_be = xraylib.ElementDensity(xraylib.SymbolToAtomicNumber("Be"))

    task = ec.ApplyAttenuators(
        inputs={
            "energy_eV": energy,
            "spectral_power": spectral_power,
            "attenuators": {
                "only": {
                    "material": "Be",
                    "thickness_mm": 2.0,
                    "density_g_cm3": rho_be,
                }
            },
        }
    )
    task.run()

    transmission = ec._transmission("Be", 2.0, rho_be, energy)

    np.testing.assert_allclose(
        task.outputs.attenuated_spectral_power,
        spectral_power * transmission,
    )
    assert task.outputs.attenuated_flux is None


def test_apply_attenuators_missing_flux_sentinel():
    if MissingData is None:
        pytest.skip("MissingData sentinel not available")

    energy = np.array([6000.0, 10000.0])
    spectral_power = np.array([3.0, 4.0])
    rho_c = xraylib.ElementDensity(xraylib.SymbolToAtomicNumber("C"))

    task = ec.ApplyAttenuators(
        inputs={
            "energy_eV": energy,
            "spectral_power": spectral_power,
            "flux": MissingData(),
            "attenuators": {
                "only": {
                    "material": "C",
                    "thickness_mm": 1.5,
                    "density_g_cm3": rho_c,
                }
            },
        }
    )

    task.run()

    transmission = ec._transmission("C", 1.5, rho_c, energy)
    np.testing.assert_allclose(
        task.outputs.attenuated_spectral_power,
        spectral_power * transmission,
    )
    assert task.outputs.attenuated_flux is None


def test_spectrum_stats_mean_and_peak():
    energy = np.array([100.0, 200.0, 300.0])
    flux = np.array([10.0, 0.0, 30.0])

    task = ec.SpectrumStats(inputs={"energy_eV": energy, "attenuated_flux": flux})
    task.run()

    assert task.outputs.mean_energy_eV == pytest.approx(200.0)
    assert task.outputs.mean_idx == 1
    assert task.outputs.pic_idx == 0
    assert task.outputs.pic_energy_eV == pytest.approx(100.0)


def test_spectrum_stats_no_valid_entries():
    energy = np.array([0.0, np.nan])
    flux = np.array([1.0, 2.0])

    task = ec.SpectrumStats(inputs={"energy_eV": energy, "attenuated_flux": flux})
    task.run()

    assert np.isnan(task.outputs.mean_energy_eV)
    assert task.outputs.mean_idx == -1
    assert np.isnan(task.outputs.pic_energy_eV)
    assert task.outputs.pic_idx == -1


def test_spectrum_stats_requires_matching_shapes():
    task = ec.SpectrumStats(
        inputs={
            "energy_eV": np.array([1.0]),
            "attenuated_flux": np.array([1.0, 2.0]),
        }
    )
    with pytest.raises(ValueError):
        task.run()
