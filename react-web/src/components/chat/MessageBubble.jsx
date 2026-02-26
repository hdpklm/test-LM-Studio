import React from 'react';
import ReactMarkdown from 'react-markdown';
import { LiveProvider, LiveEditor, LiveError, LivePreview } from 'react-live';
import { User, Bot } from 'lucide-react';

// Custom components passed to ReactLive scope
const scope = { React };

const MessageBubble = ({ message }) => {
	const isUser = message.role === 'user' || message.role === 'User';

	return (
		<div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
			<div className={`flex max-w-[85%] gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
				{/* Avatar */}
				<div className={`flex-shrink-0 w-8 h-8 rounded-md flex items-center justify-center mt-1 ${isUser ? 'bg-zinc-700' : 'bg-[#f4ba3e]/20 text-[#f4ba3e]'
					}`}>
					{isUser ? <User className="w-5 h-5 text-zinc-300" /> : <Bot className="w-5 h-5" />}
				</div>

				{/* Content */}
				<div className="flex-1 space-y-2 min-w-0">
					<div className="font-semibold text-sm text-zinc-400">
						{isUser ? 'Tú' : 'Asistente'}
					</div>

					<div className="text-zinc-200 text-sm leading-relaxed whitespace-pre-wrap">
						<ReactMarkdown
							components={{
								code({ node, inline, className, children, ...props }) {
									const match = /language-(\w+)/.exec(className || '');
									const codeContent = String(children).replace(/\n$/, '');

									// React Live interpreter for jsx/tsx/react blocks
									if (!inline && match && (match[1] === 'jsx' || match[1] === 'tsx' || match[1] === 'react')) {
										return (
											<div className="my-4 border border-zinc-700 rounded-lg overflow-hidden bg-zinc-950">
												<div className="px-3 py-1 bg-zinc-800 text-xs text-zinc-400 font-mono flex justify-between items-center border-b border-zinc-700">
													<span>React Preview</span>
												</div>
												<LiveProvider code={codeContent} scope={scope}>
													<div className="flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-zinc-700">
														<div className="w-full md:w-1/2 p-4 bg-zinc-900 overflow-auto">
															<LiveEditor className="font-mono text-sm" theme={{ plain: { color: '#e4e4e7' }, styles: [] }} />
														</div>
														<div className="w-full md:w-1/2 p-4 bg-white text-black overflow-auto min-h-[200px]">
															<LiveError className="text-red-500 text-xs mb-2 p-2 bg-red-100 rounded" />
															<LivePreview />
														</div>
													</div>
												</LiveProvider>
											</div>
										);
									}

									// Default code block
									return !inline ? (
										<div className="my-2 rounded-md overflow-hidden border border-zinc-700">
											<div className="bg-zinc-800 text-zinc-400 px-3 py-1 text-xs font-mono">{match?.[1] || 'code'}</div>
											<pre className="p-3 bg-zinc-950 overflow-x-auto text-sm">
												<code className={className} {...props}>
													{children}
												</code>
											</pre>
										</div>
									) : (
										<code className="bg-zinc-800 text-[#f4ba3e] px-1 py-0.5 rounded text-sm font-mono" {...props}>
											{children}
										</code>
									)
								},
								img({ node, src, alt }) {
									// Support for displaying images in chat
									return (
										<img src={src} alt={alt} className="max-w-full rounded-lg border border-zinc-700 my-2 shadow-lg" loading="lazy" />
									);
								},
								a({ node, href, children }) {
									return (
										<a href={href} target="_blank" rel="noopener noreferrer" className="text-[#f4ba3e] hover:underline">
											{children}
										</a>
									);
								}
							}}
						>
							{message.content}
						</ReactMarkdown>

						{/* Render explicit media from structured message if it exists (audio/video extensions) */}
						{message.mediaUrl && (
							<div className="mt-2">
								{message.mediaUrl.match(/\.(mp4|webm)$/i) ? (
									<video controls className="max-w-full rounded-lg border border-zinc-700">
										<source src={message.mediaUrl} />
									</video>
								) : message.mediaUrl.match(/\.(mp3|wav|ogg)$/i) ? (
									<audio controls className="w-full">
										<source src={message.mediaUrl} />
									</audio>
								) : null}
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	);
};

export default MessageBubble;
