import "./InfoButton.css"; // Підключаємо CSS файл

interface InfoButtonProps {
    text: React.ReactNode;
    onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

const InfoButton: React.FC<InfoButtonProps> = ({ text, onClick }) => {
  return (
    <button className="circle-btn" onClick={onClick}>
      {text}
    </button>
  );
};

export default InfoButton;