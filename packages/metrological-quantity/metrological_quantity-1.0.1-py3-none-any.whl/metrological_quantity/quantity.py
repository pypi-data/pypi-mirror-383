"""
metrological_quantity.quantity
=============================

Provides the Quantity class for arithmetic operations with physical quantities, including units and uncertainties.

Functions
---------
square_sum(value1, value2)
    Calculate the square root of the sum of squares of two values.

Classes
-------
Quantity
    Class to perform arithmetic operations with quantities, units, and uncertainties.
"""

from math import sqrt


def square_sum(value1, value2):
    """
    Calculate the square root of the sum of squares of two values.

    Parameters
    ----------
    value1 : float
        First value.
    value2 : float
        Second value.

    Returns
    -------
    float
        The square root of (value1**2 + value2**2).
    """
    return sqrt(value1 ** 2 + value2 ** 2)


class Quantity:
    """
    Class to perform simple arithmetic operations with quantities including units and uncertainties.

    Attributes
    ----------
    value : float
        The numerical value of the quantity.
    uncertainty : float
        The absolute uncertainty of the quantity.
    unit : str
        The unit of the quantity.

    Methods
    -------
    relative_uncertainty
        Returns the relative uncertainty of the quantity.
    percentage_uncertainty
        Returns the percentage uncertainty of the quantity.
    __add__(other)
        Adds two Quantity objects with the same unit.
    __sub__(other)
        Subtracts one Quantity object from another with the same unit.
    __mul__(other)
        Multiplies this Quantity object by another Quantity or a scalar.
    __rmul__(other)
        Multiplies a scalar or Quantity by this Quantity object (right-hand multiplication).
    __truediv__(other)
        Divides this Quantity object by another Quantity or a scalar.
    """

    def __init__(self, value, uncertainty, unit, relative_uncertainty=False):
        """
        Initialize a Quantity object with value, uncertainty, and unit.

        Parameters
        ----------
        value : float
            The numerical value of the quantity.
        uncertainty : float
            The uncertainty associated with the value. Must be non-negative.
        unit : str
            The unit of the quantity (e.g., 'm', 'kg').
        relative_uncertainty : bool, optional
            If True, the uncertainty is interpreted as relative (fractional) uncertainty and multiplied by the absolute value.
            If False (default), the uncertainty is interpreted as absolute uncertainty.

        Raises
        ------
        ValueError
            If uncertainty is negative.
        """
        if uncertainty < 0:
            raise ValueError('Uncertainty must be positive.')
        self.value = value
        self.unit = unit
        if relative_uncertainty:
            self.uncertainty = uncertainty * abs(value)
        else:
            self.uncertainty = uncertainty

    @property
    def relative_uncertainty(self):
        """
        Relative uncertainty of the quantity.

        Returns
        -------
        float
            The ratio of the absolute uncertainty to the value of the quantity.
            Calculated as uncertainty / value.
        """
        return self.uncertainty / self.value

    @property
    def percentage_uncertainty(self):
        """
        Percentage uncertainty of the quantity.

        Returns
        -------
        float
            The uncertainty as a percentage of the value.
            Calculated as (uncertainty / value) * 100.
        """
        return self.uncertainty / self.value * 100

    def __repr__(self):
        """
        Official string representation of the Quantity object.

        Returns
        -------
        str
            A string that recreates the Quantity object with its value, uncertainty, and unit.
            Format: Quantity(value, uncertainty, 'unit')
        """
        return f'Quantity({self.value}, {self.uncertainty}, \'{self.unit}\')'

    def __str__(self):
        """
        Human-readable string representation of the Quantity object.

        Returns
        -------
        str
            A formatted string showing the value, uncertainty, unit, and percentage uncertainty.
            Format: '<value> ± <uncertainty> <unit> (<percentage_uncertainty>%)'
        """
        return f'{self.value} \u00B1 {self.uncertainty} {self.unit} ({self.percentage_uncertainty}%)'

    def __add__(self, other):
        """
        Add two Quantity objects with the same unit.

        Parameters
        ----------
        other : Quantity
            The other Quantity object to add. Must have the same unit as self.

        Returns
        -------
        Quantity
            A new Quantity object representing the sum, with combined uncertainty.

        Raises
        ------
        ValueError
            If the units of the two quantities do not match.
        """
        if self.unit == other.unit:
            value = self.value + other.value
            uncertainty = square_sum(self.uncertainty, other.uncertainty)
            return Quantity(value=value, uncertainty=uncertainty, unit=self.unit)
        else:
            raise ValueError('Added quantities must have the same units.')

    def __sub__(self, other):
        """
        Subtract one Quantity object from another with the same unit.

        Parameters
        ----------
        other : Quantity
            The other Quantity object to subtract. Must have the same unit as self.

        Returns
        -------
        Quantity
            A new Quantity object representing the difference, with combined uncertainty.

        Raises
        ------
        ValueError
            If the units of the two quantities do not match.
        """
        if self.unit == other.unit:
            value = self.value - other.value
            uncertainty = square_sum(self.uncertainty, other.uncertainty)
            return Quantity(value=value, uncertainty=uncertainty, unit=self.unit)
        else:
            raise ValueError('Subtracted quantities must have the same units.')

    def __mul__(self, other):
        """
        Multiply this Quantity object by another Quantity or a scalar.

        Parameters
        ----------
        other : Quantity or float
            The other Quantity object or scalar to multiply by.

        Returns
        -------
        Quantity
            A new Quantity object representing the product, with combined relative uncertainty.
        """
        return self._mul(other)

    def __rmul__(self, other):
        """
        Multiply a scalar or Quantity by this Quantity object (right-hand multiplication).

        Parameters
        ----------
        other : Quantity or float
            The other Quantity object or scalar to multiply by.

        Returns
        -------
        Quantity
            A new Quantity object representing the product, with combined relative uncertainty.
        """
        return self._mul(other)

    def __truediv__(self, other):
        """
        Divide this Quantity object by another Quantity or a scalar.

        Parameters
        ----------
        other : Quantity or float
            The other Quantity object or scalar to divide by.

        Returns
        -------
        Quantity
            A new Quantity object representing the quotient, with combined relative uncertainty.
            If dividing by a Quantity, the resulting unit is a compound unit.
        """
        if isinstance(other, Quantity):
            value = self.value / other.value
            unit = f'({self.unit}/{other.unit})'
            relative_uncertainty = square_sum(self.relative_uncertainty, other.relative_uncertainty)
        else:
            value = self.value / other
            unit = self.unit
            relative_uncertainty = self.relative_uncertainty
        return Quantity(value=value, uncertainty=relative_uncertainty, unit=unit, relative_uncertainty=True)

    def _mul(self, other):
        """
        Internal method to multiply this Quantity object by another Quantity or a scalar.

        Parameters
        ----------
        other : Quantity or float
            The other Quantity object or scalar to multiply by.

        Returns
        -------
        Quantity
            A new Quantity object representing the product, with combined relative uncertainty.
            If multiplying by a Quantity, the resulting unit is a compound unit.
        """
        if isinstance(other, Quantity):
            value = self.value * other.value
            unit = f'({self.unit}·{other.unit})'
            relative_uncertainty = square_sum(self.relative_uncertainty, other.relative_uncertainty)
        else:
            value = self.value * other
            unit = self.unit
            relative_uncertainty = self.relative_uncertainty
        return Quantity(value=value, uncertainty=relative_uncertainty, unit=unit, relative_uncertainty=True)
