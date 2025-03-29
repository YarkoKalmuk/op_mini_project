import React from "react";

const Login = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-r from-blue-400 to-blue-600">
      <div className="bg-white p-10 rounded-lg shadow-2xl w-96 text-center">
        <h2 className="text-4xl font-bold text-blue-600 mb-6">Логін</h2>
        <input
          type="text"
          placeholder="Логін"
          className="w-full mb-4 p-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300"
        />
        <input
          type="password"
          placeholder="Пароль"
          className="w-full mb-6 p-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300"
        />
        <button className="w-full bg-blue-500 px-6 py-3 rounded-full text-white font-bold hover:bg-blue-600 transition duration-300">
          Увійти
        </button>
        <p className="mt-4 text-gray-600">
          Не маєш акаунту?{" "}
          <a href="/register" className="text-blue-500 hover:underline">
            Зареєструватися
          </a>
        </p>
      </div>
    </div>
  );
};

export default Login;
