import InfoButton from "./components/InfoButton"

function App() {
  const handleClick = () => {
    alert("Кнопка натиснута!");
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", marginTop: "50px" }}>
      <InfoButton text={<i style={{ fontFamily: "'Patrick Hand', cursive" }}>i</i>} onClick={handleClick} />
    </div>
  );
}

export default App;
