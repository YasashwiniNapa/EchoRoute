import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
// import { Button } from '@mui/material';
// import PlayArrowIcon from '@mui/icons-material/PlayArrow'; 
// import StopIcon from '@mui/icons-material/Stop';

const AudioRecorder = () => {
  // states to get button works & audio input
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null); 
  // save the audio blob for uploading
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    if (navigator.mediaDevices) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          mediaRecorderRef.current = new MediaRecorder(stream);
          mediaRecorderRef.current.ondataavailable = event => {
            audioChunksRef.current.push(event.data);
          };
          mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
            setAudioBlob(audioBlob);
            const audioURL = URL.createObjectURL(audioBlob);
            setAudioURL(audioURL); // audio url plays it back
            // catching bits of array 
            audioChunksRef.current = [];
          };
        })
        .catch(error => {
          console.error('Error accessing the microphone', error);
        });
    }
  }, []);

  const startRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.start();
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleUpload = async () => {
    if (!audioBlob) {
      console.error("no audio recorded");
      return;
    }

    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    try {
      // change the URL to your backend server URL
      const response = await axios.post("http://127.0.0.1:5000/transcribe", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("transcription:", response.data.transcription);
    } catch (error) {
      console.error("error uploading audio:", error);
    }
  };

  return (
    <div>
      <h2>Audio Recorder</h2>
      <button onClick={startRecording} disabled={isRecording}>
        Start Recording
      </button>
      <button onClick={stopRecording} disabled={!isRecording}>
        Stop Recording
      </button>
      {audioURL && (
        <div>
          <h3>Playback</h3>
          <audio controls>
            <source src={audioURL} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
      {audioBlob && (
        <button onClick={handleUpload}>Upload for Transcription</button>
      )}
    </div>
  );
};

export default AudioRecorder;
