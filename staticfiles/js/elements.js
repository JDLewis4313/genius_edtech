/**
 * Elements data for the periodic table
 * This provides a fallback in case the server-side data loading fails
 */
const elementData = [
  {
    "number": 1,
    "symbol": "H",
    "name": "Hydrogen",
    "atomic_mass": 1.008,
    "category": "nonmetal",
    "group": 1,
    "period": 1,
    "block": "s",
    "electron_configuration": "1s¹",
    "electronegativity": 2.20,
    "description": "Colorless, odorless, tasteless, non-toxic, highly combustible gas with the molecular formula H₂. The most abundant chemical substance in the universe."
  },
  {
    "number": 2,
    "symbol": "He",
    "name": "Helium",
    "atomic_mass": 4.0026,
    "category": "noble gas",
    "group": 18,
    "period": 1,
    "block": "s",
    "electron_configuration": "1s²",
    "electronegativity": null,
    "description": "Colorless, odorless, tasteless, non-toxic, inert, monatomic gas. The second lightest and second most abundant element in the observable universe."
  },
  // Add more elements as needed for fallback
];

/**
 * Get element data by atomic number
 * @param {number} atomicNumber - The atomic number of the element
 * @returns {object|null} - The element data or null if not found
 */
function getElementByNumber(atomicNumber) {
    return elementData.find(element => element.number === atomicNumber) || null;
}

/**
 * Get element data by symbol
 * @param {string} symbol - The symbol of the element
 * @returns {object|null} - The element data or null if not found
 */
function getElementBySymbol(symbol) {
    return elementData.find(element => element.symbol === symbol) || null;
}

/**
 * Filter elements by category
 * @param {string} category - The category to filter by
 * @returns {array} - Array of elements in the specified category
 */
function getElementsByCategory(category) {
    return elementData.filter(element => element.category === category);
}

/**
 * Calculate molar mass from a chemical formula
 * @param {string} formula - The chemical formula (e.g., "H2O", "C6H12O6")
 * @returns {object} - The calculated molar mass and steps
 */
function calculateMolarMass(formula) {
    // This is a placeholder for the molar mass calculation function
    // The actual implementation would parse the formula and calculate the mass
    return {
        formula: formula,
        molar_mass: 0,
        steps: []
    };
}