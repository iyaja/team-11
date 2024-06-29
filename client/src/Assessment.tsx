import React from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Result } from './types.ts';
import ChevronUp from "./assets/ChevronUp.tsx";
import ChevronDown from "./assets/ChevronDown.tsx";
import './Assessment.css';

export default function Assessment({ result }: { result: Result }) {
    const resultRef = React.useRef<HTMLDivElement>(null);
    const [commentIndex, setCommentIndex] = React.useState<number>(-1);

    React.useEffect(() => {
        // Scroll to the comment
        if (commentIndex >= 0 && resultRef.current) {
            // const comment = result.comments[commentIndex];
            // const start = comment.quote.start;
            // const end = comment.quote.end;
            // const text = comment.quote.text;
            // const resultElement = resultRef.current;
            // const textElement = resultElement.querySelector(`[data-start="${start}"][data-end="${end}"]`);
            // if (textElement) {
            //     textElement.scrollIntoView();
            //     textElement.classList.add("highlight");
            // }
        }
    }, [commentIndex]);

    return (
        <div className="container">
            <div ref={resultRef} className="result"><Markdown remarkPlugins={[remarkGfm]}>{result.markdown}</Markdown></div>
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
        </div>
    );
}
