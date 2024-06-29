import React from 'react';
import LogoIcon from './LogoIcon.tsx';
import ProcessingAnimation from './ProcessingAnimation.tsx';
import { Result } from './types.ts';
import Assessment from './Assessment.tsx';
import sampleJson from '../../server/sample_comments_2.json';
import './App.css';

function App() {
  const [isDragOver, setDragOver] = React.useState<boolean>(false);
  const [isProcessing, setIsProcessing] = React.useState<boolean>(false);
  const [result, setResult] = React.useState<Result | undefined>(undefined);

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsProcessing(true);
    setDragOver(false);
    setTimeout(() => {
      setIsProcessing(false);
      const sampleResult = sampleJson as Result;
      setResult(sampleResult);
    }, 2000);
  }

  if (result) {
    return <Assessment result={result} />;
  }

  return (
    <>
      <div className="logo"><LogoIcon color="#fff" /></div>
      <span className="header">Upload your environmental impact statements here for quick assessment and insights</span>
      {isProcessing 
        ? <div className="processing"><ProcessingAnimation/></div>
        : <div className={`dropzone${isDragOver ? ' drag' : ''}`} onDragEnter={() => setDragOver(true)} onDragLeave={() => setDragOver(false)} onDragOver={onDragOver} onDrop={onDrop}>
        Drop your document here
        </div>
      }
    </>
  )
}

export default App
