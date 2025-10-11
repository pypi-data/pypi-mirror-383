import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate
import scipy.interpolate

from pysolarcell.spectra import Lamp, AM0, AM15G, AM15D, LED1, LED2
from pysolarcell.materials import Material, PEROVSKITE, SILICON

# Constants
h = 6.62607015e-34  # Js
c = 299792458  # m/s
k = 1.380649e-23  # J/K
q = 1.602176634e-19  # C
sigma = 5.670374419e-8  # W/m^2/K^4
pi = np.pi
n_points = 1000  # Change to 1000 for straight lines

np.seterr(all='raise')

def PARALLEL(*cells):
    return [*cells, True]

def SERIES(*cells):
    return [*cells, False]

def set_n_points(n):
    global n_points
    n_points = n


class Layer:
    def __init__(self, name, bandgap, iqe=1, thickness: float=0, k=None, area=100, Rs=0, Rsh=np.inf, T=298, n=1, real_voc=np.inf, real_jsc=np.inf, fg=2):
        """Creates a new layer of a solar cell stack. This can be created from a thickness and absorption data or a bandgap.

        :param name: Name of the layer (str)
        :param bandgap: Bandgap of the material (float)
        :param iqe: Internal quantum efficiency (float)
        :param thickness: Thickness of the layer (nm)
        :param k: Extinction coefficient (unitless) as a function of wavelength (nm)
        :param bandgap: Bandgap energy (eV)
        """

        self.name = name
        self.bandgap = bandgap  # Note: Bandgap must be greater than 1.05 eV for 1200 nm
        self.iqe = iqe
        self.thickness = thickness
        self.k = k
        self.area = area
        self.Rs = Rs
        self.Rsh = Rsh
        self.T = T
        self.n = n
        self.real_voc = real_voc
        self.real_jsc = real_jsc
        self.fg = fg  # Emission area fraction (fg = 2 allows radiative emission from both side)

        self.properties = {}

        self.type = None

        if self.thickness != 0 and self.k is not None:
            self.type = 'absorption'
        else:
            self.type = 'bandgap'

    def __repr__(self):
        return f'Layer({self.name})'

    @staticmethod
    def from_material(name, material: Material, thickness: float, *args):
        """Create a layer from a given material of some thickness

        :param name: Name of the layer
        :param material: Material of the layer
        :param thickness: Thickness of the layer (nm)
        :param args: Other parameters
        :return: Layer of the given material
        """

        return Layer(name, material.bandgap, thickness, material.k, *args)

    def to_solar_cell(self, light_spectrum: Lamp):
        """Converts the layer to a solar cell using a light spectrum

        :param light_spectrum: The incident spectrum
        :return: The solar cell from the layer AND changes the spectrum in-place
        """
        Eg = self.bandgap * q  # Energy in J
        u = Eg / (k * self.T)

        if self.type == 'bandgap':
            lambda_g = h * c / Eg * 1e9  # Bandgap wavelength in nm
            assert min(light_spectrum.wavelengths()) < lambda_g < max(light_spectrum.wavelengths()), 'This bandgap lies outside the spectrum range!'
            EQE = np.zeros_like(light_spectrum.wavelengths(), dtype=np.float64)
            EQE[light_spectrum.wavelengths() < lambda_g] = self.iqe

        if self.type == 'absorption':
            # I/I0 = exp(-4 pi k x / lambda) with x in nm and lambda in nm
            EQE = (1 - np.exp(-4 * pi * self.k(light_spectrum.wavelengths()) * self.thickness / light_spectrum.wavelengths())) * self.iqe

        spectral_response = q * light_spectrum.wavelengths() / (h * c) * EQE * 1e-9

        Jsc = scipy.integrate.trapezoid(light_spectrum.irradiances() * spectral_response,
                                        light_spectrum.wavelengths()) / 10  # mA/cm^2

        if self.real_voc == np.inf:
            # Diode saturation current (mA/cm^2)
            # J0 = ((15 * q * sigma * self.T ** 3) / (k * pi ** 4)
            #       * scipy.integrate.quad(lambda x: x ** 2 / (np.exp(x) - 1), u, 500)[0] / 10)
            integral = lambda x: (x ** 2 + 2 * x + 2) / np.exp(x)  # Approximation for above integral
            J0 = self.fg * (15 * q * sigma * self.T ** 3) / (k * pi ** 4) * integral(u) / 10
        else:
            J0 = self.real_jsc / (np.exp(q * self.real_voc / (self.n * k * self.T)) - 1)

        Voc = self.n * k * self.T / q * np.log(Jsc / J0 + 1)

        solar_cell = SolarCell(Jsc, Voc, area=self.area, Rs=self.Rs, Rsh=self.Rsh, T=self.T, n=self.n)

        self.properties['Jsc'] = Jsc
        self.properties['Voc'] = Voc
        self.properties['JV'] = solar_cell.jv()
        self.properties['FF'] = solar_cell.ff()
        self.properties['MPP'] = solar_cell.mpp()
        self.properties['EQE'] = (light_spectrum.wavelengths(), light_spectrum.irradiances() * EQE)
        self.properties['Incident Power'] = light_spectrum.total_power()

        # Calculate light after the cell
        light_spectrum.update(EQE)

        return solar_cell

    def eqe(self):
        """Returns the external quantum efficiency of the cell as a function of wavelength

        :return: Quantum efficiency (%) as a function of wavelength
        """

        if 'EQE' not in self.properties.keys():
            print('Warning: You must convert this layer to a solar cell first.')

        EQE = self.properties['EQE']
        return EQE[0], EQE[1] / AM15G().irradiances() * 100

    def jv(self):
        """Returns the JV curve of the cell as a tuple (voltages, currents)

        :return: JV curve as a tuple (voltages, currents)
        """

        if 'JV' not in self.properties.keys():
            print('Warning: You must convert this layer to a solar cell first.')

        return self.properties['JV']

    def ff(self):
        if 'FF' not in self.properties.keys():
            print('Warning: You must convert this layer to a solar cell first.')

        return self.properties['FF']

    def mpp(self):
        if 'MPP' not in self.properties.keys():
            print('Warning: You must convert this layer to a solar cell first.')

        return self.properties['MPP']

    def efficiency(self):
        """Returns the efficiency of the cell assuming AM1.5G spectrum

        :return: Efficiency (%)
        """
        if 'MPP' not in self.properties.keys():
            print('Warning: You must convert this layer to a solar cell first.')

        return self.properties['MPP'][1] / self.properties['Incident Power'] * 100

    def max_power(self):
        """Returns the maximum power in mW/cm^2

        :return: Maximum power in mW/cm^2
        """
        return self.mpp()[1]


class Stack:
    def __init__(self, layers, lamp: Lamp=None, name=''):
        """Creates a stack of cells. Usage SERIES(layer1, PARALLEL(layer2, layer3))

        :param layers: List of layers
        :param lamp: The initial light source
        :param name: The name of the stack
        """

        self.name = name
        self.layers = layers
        self.lamp = lamp
        self.flattened_layers = []

        if self.lamp is None:
            self.lamp = AM15G()

        self.incident_power = scipy.integrate.trapezoid(self.lamp.irradiances(), self.lamp.wavelengths() / 10)

        self.jv_curve = None
        self.properties = {}

    def flatten(self, layers, parallel=False):
        if isinstance(layers, Layer):
            self.flattened_layers.append(layers)

            # Convert layer to IV curve
            cell = layers.to_solar_cell(self.lamp)

            # if parallel:
            #     return cell.jv()

            currents = cell.currents
            voltages = cell.V(currents)
            return voltages, cell.ItoJ(currents)

        if isinstance(layers, list):
            assert len(layers) == 3, 'Stack formatted incorrectly'

            jv1 = self.flatten(layers[0], parallel=layers[2])
            jv2 = self.flatten(layers[1], parallel=layers[2])
            if layers[2]:
                return Stack.add_jv_parallel(jv1, jv2)

            return Stack.add_jv_series(jv1, jv2)

        raise ValueError('Stack formatted incorrectly')


    def jv(self):
        # Use precomputed JV curve
        if 'JV' not in self.properties.keys():
            self.properties['JV'] = self.flatten(self.layers)

        return self.properties['JV']

    def eqe(self):
        if 'EQE' not in self.properties.keys():
            wavelengths = None
            EQE = None
            for layer in self.flattened_layers:
                if EQE is None:
                    wavelengths, EQE = layer.eqe()
                else:
                    EQE += layer.eqe()[1]

            self.properties['EQE'] = (wavelengths, EQE)

        return self.properties['EQE']

    def mpp(self):
        """Finds the maximum power point of the solar cell stack

        :return: Tuple of ((voltage, current), maximum power)
        """

        if 'MPP' not in self.properties.keys():

            voltages, currents = self.jv()

            max_index = np.argmax(voltages * currents)

            self.properties['MPP'] = ((voltages[max_index], currents[max_index]),
                                      voltages[max_index] * currents[max_index])

        return self.properties['MPP']

    def ff(self):
        """Finds the fill factor of the solar cell stack

        :return: Fill factor of the solar cell stack (%)
        """

        if 'FF' not in self.properties.keys():
            voltages, currents = self.jv()
            jv_func = scipy.interpolate.interp1d(voltages, currents, fill_value='extrapolate')
            jsc = jv_func(0)
            voc = voltages[np.argmin(np.abs(currents))]

            self.properties['Jsc'] = jsc
            self.properties['Voc'] = voc

            self.properties['FF'] = self.mpp()[1] / (jsc * voc) * 100

        return self.properties['FF']

    def voc(self):
        if 'Voc' not in self.properties.keys():
            self.ff()

        return self.properties['Voc']

    def jsc(self):
        if 'Jsc' not in self.properties.keys():
            self.ff()

        return self.properties['Jsc']

    def efficiency(self):
        return self.mpp()[1] / self.incident_power * 100

    def solve(self, verbose=True):
        self.jv()
        self.eqe()
        self.mpp()
        self.ff()

        if verbose:
            print('-' * 6 + self.name + '-' * 6)
            print(f'Voc = {self.properties['Voc']:.2f} V')
            print(f'Jsc = {self.properties['Jsc']:.2f} mA/cm^2')
            print(f'Efficiency = {self.efficiency():.2f}%')
            print(f'FF = {self.properties['FF']:.2f}%')
            print('-' * (len(self.name) + 12))

        return self.properties


    @staticmethod
    def add_jv_parallel(jv1, jv2):
        """Adds IV curves (tuples of voltage, current) in parallel

        :param jv1: First IV curve
        :param jv2: Second IV curve
        :return: New IV curve (tuple of voltage, current)
        """

        j1 = scipy.interpolate.interp1d(*jv1, fill_value='extrapolate')
        j2 = scipy.interpolate.interp1d(*jv2, fill_value='extrapolate')

        voltages = np.linspace(0, min(max(jv1[0]), max(jv2[0])) + 0.05, n_points)
        j = j1(voltages) + j2(voltages)

        return voltages, j

    @staticmethod
    def add_jv_series(jv1, jv2):
        """Adds IV curves (tuples of voltage, current) in series

        :param jv1: First IV curve
        :param jv2: Second IV curve
        :return: New IV curve (tuple of voltage, current)
        """

        v1 = scipy.interpolate.interp1d(jv1[1], jv1[0], fill_value='extrapolate')
        v2 = scipy.interpolate.interp1d(jv2[1], jv2[0], fill_value='extrapolate')

        currents = np.linspace(0, min(max(jv1[1]), max(jv2[1])) + 0.05, n_points)
        voltages = v1(currents) + v2(currents)

        return voltages, currents


class SolarCell:
    def __init__(self, Jsc, Voc, area=100, Rs=0, Rsh=np.inf, T=298, n=1):
        """Class representing a solar cell

        :param Jsc: Ideal short circuit current density (mA/cm^2)
        :param Voc: Ideal open circuit voltage (V)
        :param area: Area of cell (cm^2)
        :param Rs: Series resistance (Ohm cm^2)
        :param Rsh: Shunt resistance (Ohm cm^2)
        :param T: Temperature
        :param n: Ideality factor
        """

        self.Isc = Jsc * area / 1000  # Ideal short circuit current in mA/cm^2
        self.Jsc = Jsc
        self.Voc = Voc  # Ideal open circuit voltage in V
        self.area = area  # Area in cm^2
        self.Rs = Rs / area
        self.Rsh = Rsh / area
        self.T = T
        self.n = n

        self.voltages = np.linspace(0, self.Voc, n_points)
        self.currents = np.linspace(0, self.Isc, n_points)
        self.I0 = self.Isc / (np.exp(q * self.Voc / (self.n * k * self.T)))

        self.I = None
        self.V = None
        self.calculate_currents()
        self.calculate_voltages()

    def calculate_currents(self):
        """Returns an array of currents
        """

        if self.Rs == 0 and self.Rsh == np.inf:
            self.I = lambda v: self.Isc - self.I0 * (np.exp(q * v / (self.n * k * self.T)) - 1)
            return

        I = sp.Symbol('I')
        result = np.zeros_like(self.voltages, dtype=np.float64)

        for index, v in enumerate(self.voltages):
            guess = self.Isc - self.I0 * (sp.exp(q * v / (self.n * k * self.T)) - 1)
            result[index] = sp.nsolve(self.Isc
                                          - self.I0 * (sp.exp((v + I * self.Rs) / (self.n * k * self.T / q)) - 1)
                                          - (v + I * self.Rs) / self.Rsh - I, guess)

        self.I = scipy.interpolate.interp1d(self.voltages, result, fill_value='extrapolate')

    def calculate_voltages(self):
        """Returns an array of voltages
        """

        if self.Rs == 0 and self.Rsh == np.inf:
            self.V = lambda i: (self.n * k * self.T) / q * np.log((self.Isc - i) / self.I0 + 1)
            return

        V = sp.Symbol('V')
        result = np.zeros_like(self.currents, dtype=np.float64)

        for index, i in enumerate(self.currents):
            guess = (self.n * k * self.T) / q * sp.log((self.Isc - i) / self.I0 + 1)
            result[index] = sp.nsolve(self.Isc
                                      - self.I0 * (sp.exp((V + i * self.Rs) / (self.n * k * self.T / q)) - 1)
                                      - (V + i * self.Rs) / self.Rsh - i, guess)

        self.V = scipy.interpolate.interp1d(self.currents, result, fill_value='extrapolate')

    def jv(self):
        I = self.I(self.voltages)

        return self.voltages, self.ItoJ(I)

    def mpp(self):
        """Finds the maximum power point of the solar cell

        :return: Tuple of ((voltage, current), maximum power)
        """
        currents = self.I(self.voltages)
        max_index = np.argmax(self.voltages * currents)

        return (self.voltages[max_index], self.ItoJ(currents[max_index])), self.voltages[max_index] * currents[
            max_index]

    def ff(self):
        """Finds the fill factor of the solar cell

        :return: Fill factor of the solar cell (%)
        """

        voltages, currents = self.jv()
        jv_func = scipy.interpolate.interp1d(voltages, currents, fill_value='extrapolate')
        jsc = jv_func(0)
        voc = voltages[np.argmin(np.abs(currents))]

        return self.mpp()[1] / (jsc * voc) * 100

    def ItoJ(self, current):
        return current * 1000 / self.area

    @staticmethod
    def mpp_from_jv(voltages, currents):
        """Finds the maximum power point from a JV curve

        :param voltages: Voltage points
        :param currents: Current points (mA/cm^2)
        :return: Tuple of ((voltage, current), maximum power)
        """
        max_index = np.argmax(voltages * currents)
        max_power = voltages[max_index] * currents[max_index]
        # print(f'Maximum Power: {max_power} W')

        return (voltages[max_index], currents[max_index]), max_power

    @staticmethod
    def add_parallel(cell1: 'SolarCell', cell2: 'SolarCell'):
        """Returns the JV curve of two solar cells in parallel

        :param cell1: First solar cell
        :param cell2: Second solar cell
        :return: Tuple of (voltages, currents)
        """

        voltages = np.linspace(0, min(cell1.Voc, cell2.Voc) + 0.05, n_points)
        currents = cell1.ItoJ(cell1.I(voltages)) + cell2.ItoJ(cell2.I(voltages))

        return voltages, currents

    @staticmethod
    def add_series(cell1: 'SolarCell', cell2: 'SolarCell'):
        """Returns the JV curve of two solar cells in series

        :param cell1: First solar cell
        :param cell2: Second solar cell
        :return: Tuple of (voltages, currents)
        """

        currents = np.linspace(0, min(cell1.Isc, cell2.Isc) + 0.05, n_points)
        voltages = cell1.V(currents) + cell2.V(currents)

        return voltages, cell1.ItoJ(currents)


def plot_iv(*layers, figax=None):
    """Plots the JV curve for all layers in layers

    :param layers: The list of layers or stacks to plot
    :param figax: Tuple of figure and axes (optionaL)
    :return: Figure and axes for further modification
    """
    if figax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    else:
        fig, ax = figax

    for layer in layers:
        ax.plot(*layer.jv(), label=layer.name)

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(loc='best')
    ax.set_xlabel('Voltage (V)')
    ax.set_ylabel('Current Density ($mA/cm^2$)')
    fig.tight_layout()

    return fig, ax


def plot_eqe(*layers, figax=None):
    """Plots the external quantum efficiency for all layers in layers

    :param layers: The list of layers or stacks to plot
    :param figax: Tuple of figure and axes (optionaL)
    :return: Figure and axes for further modification
    """
    if figax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    else:
        fig, ax = figax

    for layer in layers:
        ax.plot(*layer.eqe(), label=layer.name)
        ax.fill_between(*layer.eqe(), 0, alpha=0.2)

    ax.legend()
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('EQE (%)')
    fig.tight_layout()

    return fig, ax

if __name__ == '__main__':
    import pandas as pd
    # layer1 = Layer('Cell 1 (1.71 eV)', bandgap=1.71, iqe=1, Rs=0, Rsh=np.inf)
    # layer2 = Layer('Cell 2 (1.10 eV)', bandgap=1.1, iqe=1, Rs=0, Rsh=np.inf)
    # layer1 = Layer('Cell 1 (3.00 eV)', bandgap=1.63, iqe=1)
    # layer2 = Layer('Cell 2 (1.77 eV)', bandgap=0.97, iqe=1)

    # lamp = AM15G()
    # fig, ax = lamp.plot()
    # lamp2 = lamp.modify_clarity(0.5)
    # lamp2.plot(figax=(fig, ax))
    # lamp3 = Lamp.from_smarts(2025, 6, 21, 12, 51.5, 0, 0, 0)
    # lamp3.plot(figax=(fig, ax))
    # parallel = Stack(PARALLEL(layer1, layer2), name='Parallel', lamp=AM15G())
    # series = Stack(SERIES(layer1, layer2), name='Series')

    # cell1 = Stack(layer1, name='Cell 1')
    # cell2 = Stack(layer2, name='Cell 2')

    # parallel.solve()
    # series.solve()
    # print(layer1.properties['Voc'])
    # print(series.properties)
    # cell1.solve()
    # cell2.solve()

    # fig, ax = plot_iv(layer1, layer2, series)
    # ax.set_xlim([0, 2])
    # plot_iv(cell1)
    # plt.show()
    #
    # plot_eqe(layer1, layer2, parallel)
    # plt.show()

    # layer = Layer('Cell', 1.34)
    # cell = Stack(layer, name='Single Junction')
    # cell.solve()
    #
    # bandgaps = np.linspace(0.77, 3, 500)
    # powers = np.zeros_like(bandgaps)
    # for i, bandgap in enumerate(bandgaps):
    #     layer = Layer('Cell', bandgap=bandgap, iqe=1, Rs=0, Rsh=np.inf)
    #     cell = Stack(layer, name='Stack')
    #
    #     powers[i] = cell.efficiency()
    #
    # plt.plot(bandgaps, powers)
    # plt.show()
    #
    # print(max(powers))
    # print(bandgaps[np.argmax(powers)])

    # cell1 = Layer('Cell 1', 1.4605263157894737, iqe=1)
    # cell2 = Layer('Cell 2',1.3578947368421053, iqe=1)
    # cell3 = Layer('Cell 3', 1.2552631578947369, iqe=1)
    # parallel = Stack(PARALLEL(PARALLEL(cell1, cell2), cell3))
    # series = Stack(SERIES(SERIES(cell1, cell2), cell3))
    #
    # mixed1 = Stack(PARALLEL(SERIES(cell1, cell2), cell3))
    # mixed2 = Stack(SERIES(PARALLEL(cell1, cell2), cell3))
    # mixed3 = Stack(PARALLEL(cell1, SERIES(cell2, cell3)))
    # mixed4 = Stack(SERIES(cell1, PARALLEL(cell2, cell3)))
    #
    # mixed4.solve()

    # layer1 = Layer('Cell 1 (3.00 eV)', bandgap=1.63, iqe=1, Rs=0, Rsh=np.inf)
    # layer2 = Layer('Cell 2 (1.77 eV)', bandgap=0.96, iqe=1, Rs=0, Rsh=np.inf)
    #
    # parallel = Stack(PARALLEL(layer1, layer2), name='Parallel')
    # series = Stack(SERIES(layer1, layer2), name='Series')
    # # cell1 = Stack(layer1, name='Cell 1')
    # # cell2 = Stack(layer2, name='Cell 2')
    #
    # parallel.solve()
    # series.solve()
    # # cell1.solve()
    # # cell2.solve()
    #
    # fig, axs = plt.subplots(1, 2)
    #
    # fig, ax = plot_iv(layer1, layer2, parallel, series, figax=(fig, axs[0]))
    # # ax.set_xlim([0, 2])
    # # plot_iv(cell1)
    # plot_iv(layer1, layer2, parallel, series, figax=(fig, axs[1]))
    #
    # plot_eqe(layer1, layer2, parallel)
    # plt.show()

    #


# TODO: Reflectance, recombination, diffusion length