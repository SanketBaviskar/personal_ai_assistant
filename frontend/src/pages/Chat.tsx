import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, Send, Plus, MessageSquare } from "lucide-react";
import axios from "axios";

interface Message {
	role: "user" | "assistant";
	content: string;
}

interface Conversation {
	id: number;
	title: string;
	updated_at: string;
}

import { useGoogleLogin } from "@react-oauth/google";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const Chat: React.FC = () => {
	const navigate = useNavigate();
	const [input, setInput] = useState("");
	const [messages, setMessages] = useState<Message[]>([]);
	const [loading, setLoading] = useState(false);
	const [conversationId, setConversationId] = useState<number | null>(null);
	const [conversations, setConversations] = useState<Conversation[]>([]);
	const [isDriveConnected, setIsDriveConnected] = useState(false);
	const [syncing, setSyncing] = useState(false);

	const handleLogout = () => {
		localStorage.removeItem("token");
		navigate("/login");
	};

	const fetchUser = async () => {
		try {
			const token = localStorage.getItem("token");
			const res = await axios.get(`${API_URL}/api/v1/users/me`, {
				headers: { Authorization: `Bearer ${token}` },
			});
			setIsDriveConnected(res.data.google_drive_connected);
		} catch (error) {
			console.error("Failed to fetch user", error);
		}
	};

	const fetchConversations = async () => {
		try {
			const token = localStorage.getItem("token");
			const res = await axios.get(
				`${API_URL}/api/v1/chat/conversations`,
				{
					headers: { Authorization: `Bearer ${token}` },
				}
			);
			setConversations(res.data);
		} catch (error) {
			console.error("Failed to fetch conversations", error);
		}
	};

	const fetchMessages = async (id: number) => {
		try {
			const token = localStorage.getItem("token");
			const res = await axios.get(
				`${API_URL}/api/v1/chat/${id}/messages`,
				{
					headers: { Authorization: `Bearer ${token}` },
				}
			);
			setMessages(res.data);
			setConversationId(id);
		} catch (error) {
			console.error("Failed to fetch messages", error);
		}
	};

	const connectDrive = useGoogleLogin({
		onSuccess: async (codeResponse) => {
			try {
				const token = localStorage.getItem("token");
				await axios.post(
					`${API_URL}/api/v1/auth/google-drive`,
					{
						code: codeResponse.code,
						redirect_uri: window.location.origin, // or 'postmessage' depending on setup
					},
					{
						headers: { Authorization: `Bearer ${token}` },
					}
				);
				setIsDriveConnected(true);
				alert("Google Drive connected!");
			} catch (error) {
				console.error("Failed to connect drive", error);
				alert("Failed to connect Google Drive");
			}
		},
		flow: "auth-code",
		scope: "https://www.googleapis.com/auth/drive.readonly",
	});

	const syncDrive = async () => {
		setSyncing(true);
		try {
			const token = localStorage.getItem("token");
			const res = await axios.post(
				`${API_URL}/api/v1/drive/sync`,
				{},
				{
					headers: { Authorization: `Bearer ${token}` },
				}
			);
			alert(res.data.message);
		} catch (error) {
			console.error("Sync failed", error);
			alert("Sync failed");
		} finally {
			setSyncing(false);
		}
	};

	useEffect(() => {
		fetchConversations();
		fetchUser();
	}, []);

	const sendMessage = async () => {
		if (!input.trim()) return;

		const userMsg: Message = { role: "user", content: input };
		setMessages((prev) => [...prev, userMsg]);
		setInput("");
		setLoading(true);

		try {
			const token = localStorage.getItem("token");
			const res = await axios.post(
				`${API_URL}/api/v1/chat/`,
				{
					query: input,
					conversation_id: conversationId, // Send current ID (or null)
				},
				{
					headers: { Authorization: `Bearer ${token}` },
				}
			);

			const assistantMsg: Message = {
				role: "assistant",
				content: res.data.response,
			};
			setMessages((prev) => [...prev, assistantMsg]);

			// Update conversation ID from response
			if (res.data.conversation_id) {
				setConversationId(res.data.conversation_id);
				// Refresh list if it was a new conversation
				if (!conversationId) {
					fetchConversations();
				}
			}
		} catch (error) {
			console.error("Chat error", error);
			setMessages((prev) => [
				...prev,
				{
					role: "assistant",
					content: "Error: Could not get response.",
				},
			]);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="flex h-screen bg-gray-900 text-white">
			{/* Sidebar */}
			<div className="w-64 bg-gray-800 p-4 flex flex-col border-r border-gray-700">
				<div className="mb-6">
					<h1 className="text-xl font-bold">AI Assistant</h1>
				</div>
				<button
					onClick={() => {
						setConversationId(null);
						setMessages([]);
					}}
					className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 p-3 rounded-lg mb-4 transition-colors w-full"
				>
					<Plus size={20} />
					<span>New Chat</span>
				</button>

				{/* Drive Integration */}
				<div className="mb-4 p-3 bg-gray-700 rounded-lg">
					<h3 className="text-sm font-semibold mb-2 text-gray-300">
						Integrations
					</h3>
					{!isDriveConnected ? (
						<button
							onClick={() => connectDrive()}
							className="flex items-center gap-2 bg-white text-gray-900 hover:bg-gray-100 p-2 rounded w-full text-sm font-medium transition-colors"
						>
							<img
								src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg"
								alt="Drive"
								className="w-4 h-4"
							/>
							Connect Drive
						</button>
					) : (
						<div className="space-y-2">
							<div className="flex items-center gap-2 text-green-400 text-sm">
								<span className="w-2 h-2 bg-green-400 rounded-full"></span>
								Drive Connected
							</div>
							<button
								onClick={syncDrive}
								disabled={syncing}
								className="flex items-center justify-center gap-2 bg-gray-600 hover:bg-gray-500 p-2 rounded w-full text-sm transition-colors disabled:opacity-50"
							>
								{syncing ? "Syncing..." : "Sync Files"}
							</button>
						</div>
					)}
				</div>

				<div className="flex-1 overflow-y-auto">
					<div className="text-gray-400 text-sm mb-2">Recent</div>
					{conversations.map((conv) => (
						<div
							key={conv.id}
							onClick={() => fetchMessages(conv.id)}
							className={`flex items-center gap-2 p-2 hover:bg-gray-700 rounded cursor-pointer text-gray-300 ${
								conversationId === conv.id ? "bg-gray-700" : ""
							}`}
						>
							<MessageSquare size={16} />
							<span className="truncate">
								{conv.title || `Conversation ${conv.id}`}
							</span>
						</div>
					))}
				</div>
				<div className="mt-auto pt-4 border-t border-gray-700">
					<button
						onClick={handleLogout}
						className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors w-full p-2 rounded hover:bg-gray-700"
					>
						<LogOut size={18} />
						<span>Log out</span>
					</button>
				</div>
			</div>

			{/* Main Chat Area */}
			<div className="flex-1 flex flex-col">
				<div className="flex-1 overflow-y-auto p-6 space-y-6">
					{messages.length === 0 && (
						<div className="flex flex-col items-center justify-center h-full text-gray-500">
							<h2 className="text-2xl font-semibold mb-2">
								How can I help you today?
							</h2>
						</div>
					)}
					{messages.map((msg, idx) => (
						<div
							key={idx}
							className={`flex ${
								msg.role === "user"
									? "justify-end"
									: "justify-start"
							}`}
						>
							<div
								className={`max-w-3xl p-4 rounded-lg ${
									msg.role === "user"
										? "bg-blue-600"
										: "bg-gray-700"
								}`}
							>
								<p className="whitespace-pre-wrap">
									{msg.content}
								</p>
							</div>
						</div>
					))}
					{loading && (
						<div className="flex justify-start">
							<div className="max-w-3xl p-4 rounded-lg bg-gray-700 animate-pulse">
								<p>Thinking...</p>
							</div>
						</div>
					)}
				</div>

				{/* Input Area */}
				<div className="p-4 bg-gray-800 border-t border-gray-700">
					<div className="max-w-4xl mx-auto relative">
						<input
							type="text"
							value={input}
							onChange={(e) => setInput(e.target.value)}
							onKeyDown={(e) =>
								e.key === "Enter" && sendMessage()
							}
							placeholder="Message Personal AI..."
							className="w-full bg-gray-700 text-white rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
						/>
						<button
							onClick={sendMessage}
							disabled={loading || !input.trim()}
							className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
						>
							<Send size={20} />
						</button>
					</div>
					<div className="text-center text-xs text-gray-500 mt-2">
						AI can make mistakes. Check important info.
					</div>
				</div>
			</div>
		</div>
	);
};

export default Chat;
