import React from "react";

const Login = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-blue-100">
      <div className="bg-white p-10 rounded-lg shadow-lg w-96 text-center">
        <h2 className="text-3xl font-bold mb-6">Логін</h2>
        <input
          type="text"
          placeholder="Логін"
          className="w-full mb-4 p-3 rounded-md border border-gray-300"
        />
        <input
          type="password"
          placeholder="Пароль"
          className="w-full mb-4 p-3 rounded-md border border-gray-300"
        />
        <button className="bg-yellow-400 px-6 py-3 rounded-full text-white font-bold">
          Увійти
        </button>
        <p className="mt-4">
          Не маєш акаунту? <a href="/register" className="text-blue-600">Зареєструватися</a>
        </p>
      </div>
    </div>
  );
};

export default Login;
