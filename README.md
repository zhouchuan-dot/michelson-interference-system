# Michelson Interference Experiment System

## Project Overview

A PyQt5-based auxiliary system for the Michelson interference experiment, consisting of three core modules:

- **Fringe Counter & Video Processing**: High-precision automatic fringe recognition and counting
- **Interference Simulation**: Real-time interference fringe visualization with adjustable parameters
- **Smart Q&A Assistant**: Experimental knowledge base and intelligent fringe diagnosis

## File Description

| File | Description |
|------|-------------|
| `fringe_counter.py` | High-precision fringe counting system. Supports video import, frame-by-frame processing, fringe enhancement, real-time counting, and optical path difference calculation |
| `interference_simulator.py` | Interference fringe simulator. Supports adjusting laser wavelength and movable mirror position, with real-time display of interference patterns and intensity distribution |
| `qa_assistant.py` | Experimental Q&A assistant. Built-in FAQ knowledge base, supports fringe type intelligent diagnosis and adjustment suggestions |

## Environment Requirements

- Python 3.7+
- Operating System: Windows / macOS / Linux

## Installation

```bash
pip install -r requirements.txt
```

## Usage Guide

### 1. Fringe Counter System

```bash
python fringe_counter.py
```

- Click **Import Video** to load an experimental video
- Click **Play Video** to preview the video
- Click **Process Video** to process the video (grayscale conversion, enhancement)
- Adjust the **Contrast** and **Sensitivity** sliders to optimize processing results
- Click **Start Counting** to begin fringe counting
- The right panel displays in real-time: current fringe count, total moved fringes, optical path difference, and movement direction

### 2. Interference Simulator

```bash
python interference_simulator.py
```

- Drag the **Wavelength** slider to adjust the laser wavelength (400–700 nm)
- Drag the **M2 Position** slider to adjust the movable mirror position (0–4 μm)
- Observe the real-time changes in interference patterns and intensity distribution curves
- Click **Save Image** to save the current interference pattern
- Click **Show/Hide Text** to toggle information display

### 3. Q&A Assistant

```bash
python qa_assistant.py
```

- Click an item in the left FAQ list to view the answer
- Enter a question in the input box and click **Ask** to get an intelligent response
- Upload a fringe image, select the fringe type, and click **Start Diagnosis** to get a diagnosis report

## Supported Fringe Type Diagnosis

| Fringe Type | Diagnosis |
|-------------|-----------|
| Perfect circular fringes | Equal inclination interference, ideal state, ready for wavelength measurement |
| Elliptical fringes | Arms not perfectly perpendicular, fine-tuning of screws needed |
| Straight fringes | Equal thickness interference (air wedge), suitable for thin film thickness measurement |
| Curved fringes | Mirror surface irregularity or optical element defects |
| Blurry / shaking fringes | Environmental vibration or unstable light source |
| Too dense fringes | Excessive angle between mirrors or too large optical path difference |

## Physical Parameters

- Default laser wavelength: 632.8 nm (He-Ne laser)
- Optical path difference formula: ΔL = N × λ/2
- Interference types: Equal inclination interference (circular fringes), Equal thickness interference (straight fringes)

## Project Structure

```
michelson-interference-system/
├── README.md
├── requirements.txt
├── .gitignore
├── fringe_counter.py          # Fringe counting system
├── interference_simulator.py  # Interference simulation
└── qa_assistant.py            # Q&A assistant
```

## Notes

1. Video files are recommended to be in `.mp4` or `.avi` format
2. Keep the environment stable and minimize vibrations during fringe counting
3. The movable mirror position in the simulation is limited to 0–4 μm for clear observation of fringe changes
4. The fringe diagnosis in the Q&A assistant is based on typical experimental phenomena; complex cases should be analyzed in combination with actual conditions

## License

MIT License

## Author

[Chuan Zhou]

## Acknowledgments

This project serves as a teaching auxiliary tool for the Michelson interference experiment. Thanks to the support and guidance of the related course.
