import React from 'react';
import { HashRouter } from 'react-router-dom';
import { ChatProvider } from './context/ChatContext';
import LeftDrawer from './components/layout/LeftDrawer';
import RightDrawer from './components/layout/RightDrawer';
import ChatArea from './components/chat/ChatArea';

const App = () => {
	return (
		<HashRouter>
			<ChatProvider>
				<div className="flex h-screen overflow-hidden bg-zinc-900 font-sans">
					<LeftDrawer />
					<main className="flex-1 w-full min-w-0 transition-all duration-300 relative z-0">
						<ChatArea />
					</main>
					<RightDrawer />
				</div>
			</ChatProvider>
		</HashRouter>
	);
};

export default App;
