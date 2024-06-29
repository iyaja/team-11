import React from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Result } from './types.ts';
import ChevronUp from "./assets/ChevronUp.tsx";
import ChevronDown from "./assets/ChevronDown.tsx";
import './Assessment.css';

export default function Assessment({ result }: { result: Result }) {
    const resultRef = React.useRef<HTMLDivElement>(null);
    const [commentIndex, setCommentIndex] = React.useState<number>(0);
    const [currentTab, setCurrentTab] = React.useState<'summary' | 'features' | 'comments'>('summary');

    React.useEffect(() => {
        if (currentTab !== 'comments') {
            const highlighted = resultRef.current?.querySelector("#highlighted");
            if (highlighted) {
                highlighted.removeAttribute("id");
            }
            return;
        }
        // Scroll to the comment
        if (commentIndex >= 0 && resultRef.current) {
            const comment = result.comments[commentIndex];
            const start = comment.quote.start;
            const end = comment.quote.end;
            const resultElement = resultRef.current;
            const textElement = resultElement.querySelector(`[data-start="${start}"][data-end="${end}"]`);
            if (textElement) {
                const previousHighlighted = resultElement.querySelector("#highlighted");
                if (previousHighlighted) {
                    previousHighlighted.removeAttribute("id");
                }
                textElement.scrollIntoView({ behavior: "smooth", block: "center" });
                textElement.id = "highlighted";
            }
        }
    }, [commentIndex, currentTab]);

    return (
        <div className="container">
            <div className="sidebar">
                <div className="tabs content-fade-below">
                    <button className={currentTab === 'summary' ? 'active' : ''} onClick={() => setCurrentTab('summary')}>Summary</button>
                    <button className={currentTab === 'features' ? 'active' : ''} onClick={() => setCurrentTab('features')}>Features</button>
                    <button className={currentTab === 'comments' ? 'active' : ''} onClick={() => setCurrentTab('comments')}>Comments</button>
                </div>
                <div className="summary scroll-overlay">
                    {currentTab === 'summary' && <Markdown remarkPlugins={[remarkGfm]}>{result.summary}</Markdown>}
                    {currentTab === 'comments' && (
                        <div className="comments">
                            <div className="navigation">
                                {commentIndex >= 0 && <span>{commentIndex + 1}/{result.comments.length}</span>}
                                <span>
                                    <button onClick={() => setCommentIndex(index => index <= 0 ? result.comments.length - 1 : index - 1)}><ChevronUp /></button>
                                    <button onClick={() => setCommentIndex(index => index >= result.comments.length - 1 ? 0 : index + 1)}><ChevronDown/></button>
                                </span>
                            </div>
                            {commentIndex >= 0 ? (
                                <div className="comment">{result.comments[commentIndex].comment}</div>
                            ) : (
                                <div className="instruction">Click on the buttons above to view comments</div>
                            )}
                        </div>
                    )}
                </div>
            </div>
            <div ref={resultRef} className="result scroll-overlay"><Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{result.markdown}</Markdown></div>
        </div>
    );
}
