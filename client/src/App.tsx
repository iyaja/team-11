import React from 'react';
import LogoIcon from './LogoIcon';
import ProcessingAnimation from './ProcessingAnimation';
import { Result } from './types';
import Assessment from './Assessment';
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
      setResult({
        markdown: '## Summary\n\nThis is a summary of the document.\n\n## Comments\n\nThese are the comments.',
        comments: [
          {
            quote: {
              start: 0,
              end: 10,
              text: 'This is a quote.',
            },
            comment: 'This is a comment.',
            metadata: {
              risk_factor: 'high',
            },
          },
        ],
      });
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
