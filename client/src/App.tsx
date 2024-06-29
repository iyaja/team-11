import React from 'react';
import LogoIcon from './LogoIcon.tsx';
import DocumentIcon from './assets/DocumentIcon.tsx';
import ProcessingAnimation from './ProcessingAnimation.tsx';
import { Result } from './types.ts';
import Assessment from './Assessment.tsx';
import sampleJson from '../../server/final_2.json';
import './App.css';

function App() {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [isDragOver, setDragOver] = React.useState<boolean>(false);
  const [isProcessing, setIsProcessing] = React.useState<boolean>(false);
  const [result, setResult] = React.useState<Result | undefined>(undefined);

  const onSubmit = () => {
    setIsProcessing(false);
      const sampleResult = sampleJson as Result;
      // Sort comments in descending order so that we can replace the quotes in reverse order to avoid changing the text indices
      const comments = sampleResult.comments.slice().sort((a, b) => b.quote.start - a.quote.start);
      for (let i = 0; i < comments.length; i++) {
        const comment = comments[i];
        const start = comment.quote.start;
        const end = comment.quote.end;
        const markdown = sampleResult.markdown;
        const quote = markdown.slice(start, end);
        const quoteWithAttributes = `<span data-start="${start}" data-end="${end}">${quote}</span>`;
        sampleResult.markdown = markdown.replace(quote, quoteWithAttributes);
      }
      // Sort comments in ascending order of start index when displaying
      sampleResult.comments.sort((a, b) => a.quote.start - b.quote.start);
      setResult(sampleResult);
  }

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsProcessing(true);
    setDragOver(false);
    setTimeout(() => {
      onSubmit();
    }, 2000);
  }

  const onDropzoneClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    inputRef.current?.click();
  }

  const onFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setIsProcessing(true);
    setTimeout(() => {
      onSubmit();
    }, 2000);
  }


  if (result) {
    return <Assessment result={result} />;
  }

  return (
    <>
      <div className="logo"><LogoIcon color="#fff" /></div>
      <span className="header">Streamline Your Environmental Impact Assessment</span>
      <span className="subheader">Upload statements for instant insights.</span>
      {isProcessing 
        ? <div className="processing"><ProcessingAnimation/></div>
        : <div className={`dropzone${isDragOver ? ' drag' : ''}`} onClick={onDropzoneClick} onDragEnter={() => setDragOver(true)} onDragLeave={() => setDragOver(false)} onDragOver={onDragOver} onDrop={onDrop}>
          <input
            ref={inputRef}
            type="file"
            style={{ display: 'none' }}
            accept=".doc,.docx,.pdf,.txt"
            onChange={onFileInputChange}
        />
          <DocumentIcon />
          <div className="drop-main">Upload a document</div>
          <div className="drop-sub">Drag & drop a file here<br/>or click to browse</div>
        </div>
      }
    </>
  )
}

export default App
