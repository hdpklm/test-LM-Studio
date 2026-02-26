import React from 'react';
import { useChat } from '../../context/ChatContext';
import { FileCode2, Download, ChevronRight } from 'lucide-react';

const RightDrawer = () => {
	const { rightDrawerOpen, toggleRightDrawer, generatedFiles } = useChat();

	const handleDownload = (filename) => {
		window.open(`http://localhost:8000/api/download/${filename}`, '_blank');
	};

	return (
		<div
			className={`fixed top-0 right-0 h-full bg-zinc-950/80 backdrop-blur-md border-l border-zinc-800 transition-transform duration-300 z-40 flex flex-col ${rightDrawerOpen ? 'translate-x-0 w-72' : 'translate-x-full w-72'
				}`}
		>
			<div className="p-4 flex items-center justify-between border-b border-zinc-800/50">
				<div className="flex items-center gap-2 text-zinc-100 font-semibold font-mono">
					<FileCode2 className="w-5 h-5 text-emerald-400" />
					<span>Archivos Generados</span>
				</div>
				<button onClick={toggleRightDrawer} className="text-zinc-400 hover:text-zinc-100 p-1">
					<ChevronRight className="w-5 h-5" />
				</button>
			</div>

			<div className="flex-1 overflow-y-auto p-3 space-y-3">
				{generatedFiles.length === 0 ? (
					<div className="text-zinc-500 text-sm text-center italic mt-10">No hay archivos generados</div>
				) : (
					generatedFiles.map((file, idx) => (
						<div key={idx} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 group hover:border-zinc-700 transition-colors">
							<div className="flex items-start justify-between">
								<div className="flex-1 min-w-0 pr-2">
									<h4 className="text-zinc-200 text-sm font-medium truncate">{file.filename}</h4>
									<div className="mt-2 flex items-center gap-2">
										<span className="text-[10px] uppercase font-bold tracking-wider bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded cursor-pointer hover:bg-zinc-700 transition-colors">
											v1.0 {/* En una versión real, esto se calcula */}
										</span>
									</div>
								</div>
								<button
									onClick={() => handleDownload(file.filename)}
									className="p-1.5 rounded-md bg-zinc-800 text-zinc-400 opacity-0 group-hover:opacity-100 hover:text-emerald-400 hover:bg-emerald-400/10 transition-all shrink-0"
									title="Descargar archivo"
								>
									<Download className="w-4 h-4" />
								</button>
							</div>
						</div>
					))
				)}
			</div>
		</div>
	);
};

export default RightDrawer;
