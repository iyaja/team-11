import Markdown from "react-markdown";
import { Result } from './types';
import './Assessment.css';

export default function Assessment({ result }: { result: Result }) {
    return (
        <div className="result">
            <Markdown>{result.markdown}</Markdown>
        </div>
    );
}
