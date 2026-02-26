import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
	const [leftDrawerOpen, setLeftDrawerOpen] = useState(true);
	const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
	const [historyList, setHistoryList] = useState([]);
	const [generatedFiles, setGeneratedFiles] = useState([]);
	const [currentChatId, setCurrentChatId] = useState(null);

	// Fetch initial data
	const fetchData = async () => {
		try {
			const historyRes = await axios.get('http://localhost:8000/api/history');
			setHistoryList(historyRes.data);

			const filesRes = await axios.get('http://localhost:8000/api/generated');
			setGeneratedFiles(filesRes.data);
		} catch (error) {
			console.error("Error fetching initial data", error);
		}
	};

	useEffect(() => {
		fetchData();
	}, []);

	const toggleLeftDrawer = () => setLeftDrawerOpen(prev => !prev);
	const toggleRightDrawer = () => setRightDrawerOpen(prev => !prev);

	return (
		<ChatContext.Provider value={{
			leftDrawerOpen, toggleLeftDrawer, setLeftDrawerOpen,
			rightDrawerOpen, toggleRightDrawer, setRightDrawerOpen,
			historyList, setHistoryList,
			generatedFiles, setGeneratedFiles,
			currentChatId, setCurrentChatId,
			fetchData
		}}>
			{children}
		</ChatContext.Provider>
	);
};

export const useChat = () => useContext(ChatContext);
