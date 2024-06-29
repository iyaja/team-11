import React from 'react';
import LogoIcon from './LogoIcon';
import './App.css';

function App() {
  const [isDragOver, setDragOver] = React.useState<boolean>(false);

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(false);
  }

  return (
    <>
      <div className="logo"><LogoIcon color="#fff" /></div>
      <span className="header">Upload your environmental impact statements here for quick assessment and insights</span>
      <div className={`dropzone${isDragOver ? ' drag' : ''}`} onDragEnter={() => setDragOver(true)} onDragLeave={() => setDragOver(false)} onDragOver={onDragOver} onDrop={onDrop}>
        Drop your document here
      </div>
    </>
  )
}

export default App
