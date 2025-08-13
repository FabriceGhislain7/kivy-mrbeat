# MrBeat Application Flow Documentation

This document provides detailed flowcharts showing how the MrBeat drum machine application works step-by-step, from initialization to user interaction and audio processing.

## Table of Contents

1. [Application Startup Flow](#application-startup-flow)
2. [Audio Engine Initialization](#audio-engine-initialization)
3. [UI Construction Flow](#ui-construction-flow)
4. [Sound Loading Process](#sound-loading-process)
5. [Track Creation Flow](#track-creation-flow)
6. [Step Button Interaction](#step-button-interaction)
7. [Audio Playback Flow](#audio-playback-flow)
8. [Pattern Update Process](#pattern-update-process)
9. [BPM Change Flow](#bpm-change-flow)
10. [Real-time Audio Processing](#real-time-audio-processing)

---

## Application Startup Flow

```
┌─────────────────┐
│   main.py       │
│   starts        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Kivy Config     │
│ - Window size   │
│ - Min/Max size  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Import modules  │
│ - AudioEngine   │
│ - SoundKit      │
│ - TrackWidget   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Load KV files   │
│ - mrbeat.kv     │
│ - track.kv      │
│ - indicator.kv  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create          │
│ MrBeatApp()     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ MainWidget      │
│ __init__        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Initialize      │
│ SoundKitService │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create          │
│ AudioEngine     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create Master   │
│ Mixer           │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ UI Ready        │
│ App Running     │
└─────────────────┘
```

---

## Audio Engine Initialization

```
┌─────────────────┐
│ AudioEngine     │
│ __init__()      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ pygame.mixer    │
│ pre_init()      │
│ - 44.1kHz       │
│ - 16-bit        │
│ - 1 channel     │
│ - 1024 buffer   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ pygame.mixer    │
│ init()          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create          │
│ AudioSourceOne  │
│ Shot            │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Start OneShot   │
│ Thread          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Store mixer     │
│ reference       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Audio Engine    │
│ Ready           │
└─────────────────┘
```

---

## UI Construction Flow

```
┌─────────────────┐
│ MainWidget      │
│ on_parent()     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Configure       │
│ PlayIndicator   │
│ (16 steps)      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Get track count │
│ from SoundKit   │
│ (8 tracks)      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For each track: │
│ 0 to 7          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Get Sound at    │
│ index i         │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Add Vertical    │
│ Spacing         │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create          │
│ TrackWidget     │
│ (sound, engine, │
│  steps, track)  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Add TrackWidget │
│ to layout       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Next track or   │
│ Complete        │
└─────────────────┘
```

---

## Sound Loading Process

```
┌─────────────────┐
│ SoundKitService │
│ __init__()      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create          │
│ SoundKit1All    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For each sound: │
│ - kick.wav      │
│ - snare.wav     │
│ - etc...        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Sound()         │
│ __init__        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ wave.open()     │
│ filename        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Get frame count │
│ self.nb_samples │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Read all frames │
│ as bytes        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Convert to      │
│ array('h')      │
│ 16-bit samples  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Store samples   │
│ and metadata    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Sound loaded    │
│ and ready       │
└─────────────────┘
```

---

## Track Creation Flow

```
┌─────────────────┐
│ TrackWidget     │
│ __init__()      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Store           │
│ references:     │
│ - audio_engine  │
│ - sound         │
│ - track_source  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create sound    │
│ button section  │
│ (fixed width)   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create          │
│ TrackSoundBtn   │
│ text = sound    │
│ displayname     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Bind sound btn  │
│ to trigger      │
│ method          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Add separator   │
│ image (15dp)    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create step     │
│ buttons array   │
│ (16 buttons)    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For i = 0 to 15:│
│ Create          │
│ TrackStepBtn    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Set background  │
│ based on group: │
│ i/4 % 2 == 0    │
│ ? normal1       │
│ : normal2       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Bind step btn   │
│ state change    │
│ to update       │
│ pattern         │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Add step btn    │
│ to layout       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Track complete  │
│ and functional  │
└─────────────────┘
```

---

## Step Button Interaction

```
┌─────────────────┐
│ User clicks     │
│ step button     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ ToggleButton    │
│ changes state   │
│ "normal" ↔      │
│ "down"          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Kivy triggers   │
│ bind(state=     │
│ callback)       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ on_step_button_ │
│ state() called  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Scan ALL step   │
│ buttons in      │
│ track           │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For each button:│
│ if state ==     │
│ "down": add 1   │
│ else: add 0     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Build pattern   │
│ array:          │
│ [1,0,1,0,...]   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Call track_     │
│ source.set_     │
│ steps(pattern)  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ AudioSourceTrack│
│ updates pattern │
│ immediately     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Pattern active  │
│ for next        │
│ playback cycle  │
└─────────────────┘
```

---

## Audio Playbook Flow

```
┌─────────────────┐
│ User clicks     │
│ PLAY button     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ MainWidget.     │
│ on_play_button_ │
│ pressed()       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ mixer.audio_    │
│ play()          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ AudioSourceMixer│
│ sets is_playing │
│ = True          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Master sequencer│
│ loop starts     │
│ processing      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Check if time   │
│ for next step   │
│ (step_duration) │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Process current │
│ step for all    │
│ tracks          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For each track: │
│ if pattern[step]│
│ == 1: trigger   │
│ sound           │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create pygame   │
│ Sound object    │
│ and play()      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Update step     │
│ indicator UI    │
│ via callback    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Advance to      │
│ next step       │
│ (wrap at 16)    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Continue loop   │
│ until stopped   │
└─────────────────┘
```

---

## Pattern Update Process

```
┌─────────────────┐
│ Pattern change  │
│ requested       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ AudioSourceTrack│
│ .set_steps()    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Acquire         │
│ pattern_lock    │
│ (thread safety) │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Check if new    │
│ pattern length  │
│ != current      │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ If different    │
│ length: reset   │
│ step_index = 0  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Store new       │
│ pattern as      │
│ immutable tuple │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Release         │
│ pattern_lock    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Pattern ready   │
│ for next        │
│ sequencer cycle │
└─────────────────┘
```

---

## BPM Change Flow

```
┌─────────────────┐
│ User clicks     │
│ +/- BPM button  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ MainWidget.     │
│ on_bpm()        │
│ value ± 5       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Check BPM       │
│ bounds:         │
│ 80 ≤ bpm ≤ 160  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ If valid:       │
│ mixer.set_bpm() │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ AudioSourceMixer│
│ validates       │
│ bpm ≥ min_bpm   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Acquire         │
│ mixing_lock     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Update internal │
│ bpm value       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Recalculate     │
│ step_duration   │
│ = 15.0 / bpm    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For each track: │
│ track.set_bpm() │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Each track      │
│ recalculates    │
│ timing          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Release lock    │
│ New tempo       │
│ active          │
└─────────────────┘
```

---

## Real-time Audio Processing

```
┌─────────────────┐
│ Master Sequencer│
│ Thread Running  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ time.time()     │
│ check current   │
│ timestamp       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Calculate       │
│ elapsed since   │
│ last step       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ elapsed ≥       │
│ step_duration?  │
└─────────┬───────┘
          │ YES
          v
┌─────────────────┐
│ Process step    │
│ for all tracks  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ For each track: │
│ check pattern   │
│ [current_step]  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ If pattern[i]   │
│ == 1:           │
│ trigger_audio() │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Convert samples │
│ to pygame.Sound │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ sound.play()    │
│ immediate       │
│ playback        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Update UI       │
│ step indicator  │
│ via callback    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Advance step    │
│ index, wrap     │
│ at nb_steps     │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Sleep 1ms       │
│ prevent CPU     │
│ overload        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Loop continues  │
│ until stopped   │
└─────────────────┘
```

---

## Sound Button Immediate Trigger

```
┌─────────────────┐
│ User clicks     │
│ sound button    │
│ (e.g., "KICK")  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ TrackWidget.    │
│ on_sound_button_│
│ press()         │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ audio_engine.   │
│ play_sound()    │
│ with samples    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ AudioSourceOne  │
│ Shot.set_wav_   │
│ samples()       │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Check if        │
│ running and     │
│ acquire lock    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Convert samples │
│ to appropriate  │
│ format if       │
│ needed          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Create pygame   │
│ Sound object    │
│ from audio data │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ sound.play()    │
│ immediate       │
│ playback        │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Sound plays     │
│ independently   │
│ of sequencer    │
└─────────────────┘
```

---

## Complete Application Data Flow

```
┌─────────────────┐
│     USER        │
│   INTERACTION   │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    v           v
┌─────────┐ ┌─────────┐
│  PLAY   │ │ PATTERN │
│ BUTTON  │ │ BUTTON  │
└────┬────┘ └────┬────┘
     │           │
     v           v
┌─────────┐ ┌─────────┐
│ MIXER   │ │ TRACK   │
│ CONTROL │ │ UPDATE  │
└────┬────┘ └────┬────┘
     │           │
     v           v
┌─────────────────┐
│ AUDIO SEQUENCER │
│    PROCESSING   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ PYGAME MIXER    │
│ SOUND OUTPUT    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ SYSTEM AUDIO    │
│    SPEAKERS     │
└─────────────────┘
     │
     v
┌─────────────────┐
│ USER HEARS      │
│ DRUM PATTERN    │
└─────────────────┘
```

This flowchart documentation shows exactly how each piece of the MrBeat application connects and operates, from the moment the application starts until audio is played through the speakers.