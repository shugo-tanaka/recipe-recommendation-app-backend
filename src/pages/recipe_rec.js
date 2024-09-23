import React from "react";
import "../app/globals.css";
import { useState, useEffect } from "react";

const RecipeRec = () => {
  const [ingredientList, setIngredientList] = useState([]);
  const [quantityList, setQuantityList] = useState([]);
  const [unitList, setUnitList] = useState([]);
  const [servings, setServings] = useState(1);
  const [cuisineType, setCuisineType] = useState("");
  const [cookTime, setCookTime] = useState(30);
  const [allergies, setAllergies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [ingredientInput, setIngredientInput] = useState("");
  const units = ["unit", "pcs", "g", "kg", "ml", "l", "cup", "tbsp", "tsp"]; //look for more common measurements
  const cuisineList = [
    "None",
    "Italian",
    "Chinese",
    "Mexican",
    "Japanese",
    "Indian",
    "French",
    "Thai",
    "American",
    "Spanish",
    "Greek",
    "Middle Eastern",
    "Korean",
    "Vietnamese",
    "Brazilian",
    "Turkish",
    "Moroccan",
    "Carribean",
    "Ethiopian",
    "German",
    "Peruvian",
  ];
  const [allergyInput, setAllergyInput] = useState("");

  const handleInputChange = (e) => {
    const { value } = e.target;
    setIngredientInput(value);
  };

  const handleSubmitIngredient = (e) => {
    e.preventDefault();
    console.log("New Ingredient:", ingredientInput);
    setIngredientList((prevState) => [
      ingredientInput.toLowerCase(),
      ...prevState,
    ]);
    setQuantityList((prevState) => [1, ...prevState]);
    setUnitList((prevState) => ["", ...prevState]);
    setIngredientInput("");
  };

  const handleQuantityChange = (index, e) => {
    const updatedQuantities = [...quantityList];
    updatedQuantities[index] = e.target.values;
    setQuantityList(updatedQuantities);
  };

  const handleUnitChange = (index, e) => {
    const updatedUnits = [...unitList];
    updatedUnits[index] = e.target.values;
    setUnitList(updatedUnits);
  };

  const handleRemove = (index) => {
    setIngredientList((prevState) => prevState.filter((_, i) => i != index));
    setQuantityList((prevState) => prevState.filter((_, i) => i != index));
    setUnitList((prevState) => prevState.filter((_, i) => i != index));
    // filter(_, i) -> _ represents the current value, i represents the index it is at.
  };

  const handleServingsChange = (e) => {
    setServings(e.target.value);
  };

  const handleCuisineTypeChange = (e) => {
    setCuisineType(e.target.value);
  };

  const handleCookTimeChange = (e) => {
    setCookTime(e.target.value);
  };

  const handleAllergiesChange = (e) => {
    setAllergyInput(e.target.value);
  };

  const handleAllergySubmit = (e) => {
    e.preventDefault();
    console.log("new Allergy:", allergyInput);
    setAllergies((prevState) => [...prevState, allergyInput]);
    setAllergyInput("");
  };

  const handleRemoveAllergy = (index) => {
    setAllergies((prevState) => prevState.filter((_, i) => i != index));
  };

  return (
    <div className="flex flex-col item-center justify-center">
      {/* Container for the header and the rest of the website */}
      <h1 className="header text-3xl text-center p-5">
        Recipe Recommendation Generator
      </h1>
      <div className="flex flex-row item-center justify-center pb-10">
        {/* Container for left side and right side */}
        <div className="flex flex-col item-center justify-center bg-blue-100 rounded-3xl p-7 mr-4">
          {/* Container for ingredients and additional info */}
          <div className="ingredients-list">
            {/* Container for ingredients header, input bullet, and other bullets */}
            <h2 className="ingredient-list-header text-2xl mb-2 underline">
              Ingredients:
            </h2>
            <div className="ingredient-input mr-20">
              <form onSubmit={handleSubmitIngredient}>
                <input
                  className="border blinking-cursor border-gray-300 w-full h-8 mb-2 pl-2"
                  type="text"
                  name="ingredientInput"
                  value={ingredientInput}
                  onChange={handleInputChange}
                />
              </form>
            </div>
            <div className="ingredients-bullets">
              <ul className="list-disc">
                {ingredientList.map((ingredient, index) => (
                  <li
                    key={index}
                    className="mb-1 flex items-center justify-between"
                  >
                    <span className="mr-1">
                      {index + 1}) {ingredient}
                    </span>
                    <input
                      className="border border-gray-300 p-2 ml-auto mr-2 w-14 h-8 text-right"
                      type="number"
                      value={quantityList[index]}
                      onChange={(e) => handleQuantityChange(index, e)}
                    />
                    <select
                      className="border border-gray-300 p-1 h-8"
                      value={unitList[index]}
                      onChange={(e) => handleUnitChange(index, e)}
                    >
                      {units.map((unit) => (
                        <option key={unit} value={unit}>
                          {unit}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => handleRemove(index)}
                      className="ml-2 text-red-500 hover:text-red-700 mr-40"
                      aria-label="Remove"
                    >
                      x
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="additional-info">
            {/* Container for additional info header, and the additional info input lines */}
            <h2 className="additional-info-header text-2xl mt-5 mb-2 underline">
              Additional Information:
            </h2>
            <div>
              <span>Servings: </span>
              <input
                className="border border-gray-300 p-1 mr-2 w-12 h-8"
                type="number"
                value={servings}
                onChange={handleServingsChange}
              />
            </div>
            <div className="mt-2">
              <span>Type of Cuisine: </span>
              <select
                className="border border-gray-300 p-1 mr-2 h-8"
                value={cuisineType}
                onChange={(e) => handleCuisineTypeChange(e)}
              >
                {cuisineList.map((cuisine) => (
                  <option key={cuisine} value={cuisine}>
                    {cuisine}
                  </option>
                ))}
              </select>
            </div>
            <div className="mt-2">
              <span>Max Cook Time: </span>
              <input
                className="border border-gray-300 p-1 mr-2 w-12 h-8"
                type="number"
                value={cookTime}
                onChange={handleCookTimeChange}
              />
              <span className="mr-auto"> min</span>
            </div>
            <div className="mt-2">
              <div className="flex flex-row">
                <span>Allergies: </span>
                <form onSubmit={handleAllergySubmit}>
                  <input
                    className="border border-gray-300 blinking-cursor ml-2 h-8 pl-2"
                    type="text"
                    value={allergyInput}
                    onChange={handleAllergiesChange}
                  />
                </form>
              </div>
              <div className="flex flex-wrap max-w-80 space-x-w">
                {allergies.map((allergy, index) => (
                  <div
                    key={index}
                    className="mb-1 flex items-center justify-between"
                  >
                    <span>{allergy}</span>
                    <button
                      onClick={() => handleRemoveAllergy(index)}
                      className="ml-1 text-red-500 hover:text-red-700 mr-4"
                      aria-label="Remove"
                    >
                      x
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="right-body bg-blue-100 rounded-3xl p-7">
          {/* container for recommendations header and list of recommendations */}
          <h2 className="recommendations-header text-2xl underline">
            Recommendations:
          </h2>
        </div>
      </div>
    </div>
  );
};

export default RecipeRec;
