# metrological-quantity

Basic arithmetic operations with uncertainty and units

## Overview

`metrological-quantity` is a Python package for performing arithmetic operations on physical quantities, including support for units and propagation of uncertainties. It is designed for scientific, engineering, and educational applications where measurement uncertainty and unit consistency are important.

## Features
- Create quantities with values, uncertainties, and units
- Automatic propagation of uncertainties in arithmetic operations
- Support for addition, subtraction, multiplication, and division
- Human-readable and machine-readable representations
- Error handling for invalid operations (e.g., mismatched units)

## Installation

Install with pip:

```bash
pip install metrological-quantity
```

## Usage Example

```python
from metrological_quantity import Quantity

# Create quantities
length = Quantity(10, 0.5, 'm')
width = Quantity(5, 0.2, 'm')

# Arithmetic operations
perimeter = 2 * (length + width)
area = length * width

print('Perimeter:', perimeter)
print('Area:', area)

# Uncertainty propagation
mass1 = Quantity(5, 0.1, 'kg')
mass2 = Quantity(7, 0.2, 'kg')
total_mass = mass1 + mass2
print('Total mass:', total_mass)
```

## API Reference

### Quantity

```python
Quantity(value, uncertainty, unit, relative_uncertainty=False)
```
- `value`: numerical value
- `uncertainty`: absolute or relative uncertainty
- `unit`: string representing the unit (e.g., 'm', 'kg')
- `relative_uncertainty`: if True, interprets uncertainty as relative

#### Properties
- `relative_uncertainty`: returns the relative uncertainty
- `percentage_uncertainty`: returns the percentage uncertainty

#### Methods
- `__add__`, `__sub__`, `__mul__`, `__truediv__`: arithmetic operations with uncertainty propagation

## License

This project is licensed under the GNU General Public License.

## Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request.
