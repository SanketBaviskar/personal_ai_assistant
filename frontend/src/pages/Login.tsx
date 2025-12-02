import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login: React.FC = () => {
	const navigate = useNavigate();
	const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

	const handleSuccess = async (credentialResponse: any) => {
		try {
			const { credential } = credentialResponse;
			// Send token to backend
			const res = await axios.post(
				`${API_URL}/api/v1/auth/login/google`,
				{
					token: credential,
				}
			);

			const { access_token } = res.data;
			localStorage.setItem("token", access_token);
			navigate("/chat");
		} catch (error) {
			console.error("Login failed", error);
			alert("Login failed");
		}
	};

	return (
		<div className="flex items-center justify-center h-screen bg-gray-900 text-white">
			<div className="p-8 bg-gray-800 rounded-lg shadow-lg text-center">
				<h1 className="text-3xl font-bold mb-6">
					Personal AI Assistant
				</h1>
				<p className="mb-8 text-gray-400">
					Sign in to access your knowledge base
				</p>
				<div className="flex justify-center">
					<GoogleLogin
						onSuccess={handleSuccess}
						onError={() => {
							console.log("Login Failed");
						}}
						theme="filled_black"
						shape="pill"
					/>
				</div>
			</div>
		</div>
	);
};

export default Login;
