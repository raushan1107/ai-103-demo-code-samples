# GlobalCare AI architecture

```mermaid
flowchart LR
    User[Receptionist / learner] --> UI[Streamlit server UI]
    UI --> Detect[Azure AI Language]
    UI --> Trans[Azure Translator]
    UI --> Agent[Foundry Agent Service or M1 Responses]
    Agent --> Tools[Registered read-only Python tools]
    Tools --> KB[(Fictional JSON knowledge base)]
    UI --> Speech[Azure Speech Translation / synthesis]
    UI --> Voice[Saved Foundry voice agent]
    Voice --> Live[Foundry realtime voice service]
    Live --> UI
```

Voice Agent session lifecycle:

```mermaid
stateDiagram-v2
    [*] --> ValidateConfig
    ValidateConfig --> Authenticate: Entra credential
    Authenticate --> Connect: Project + saved voice agent
    Connect --> Stream: PCM16 microphone / server events
    Stream --> Stream: transcript, output audio, interruption
    Stream --> Close: Ctrl+C / disconnect / error
    Close --> [*]: stop devices and dispose session
```

The JSON knowledge base is the only source of hospital facts. Tool outputs are returned to a model for phrasing, but the instructions require it to state when data is missing. Tool traces record only calls that the Python dispatcher actually executed.

```mermaid
sequenceDiagram
    participant U as Receptionist
    participant A as Foundry Agent
    participant T as Tool dispatcher
    participant K as Synthetic JSON KB
    U->>A: Ask hospital question
    A->>T: Function call with schema arguments
    T->>K: Execute registered lookup
    K-->>T: Record(s) or empty result
    T-->>A: FunctionCallOutput linked by call_id
    A-->>U: Grounded administrative answer
```

```mermaid
sequenceDiagram
    participant M as Microphone
    participant D as Foundry Voice Agent SDK
    participant S as Foundry Voice Service
    participant P as Speaker
    M->>D: 24-kHz mono PCM16 chunks
    D->>S: input_audio_buffer.append (Entra-authenticated WebSocket)
    S-->>D: input transcript / speech-start / response audio delta / error events
    D-->>P: 24-kHz mono PCM16 playback chunks
    Note over D,S: Server turn detection and interruption handling
```

Text Translation follows `TextTranslationClient.translate`; supported languages are requested with `get_supported_languages` and should be cached by the application. Transliteration changes script while preserving a language's spoken form (for example kana to Latin), whereas translation changes meaning into another language.

```mermaid
flowchart LR
    Text[Text + source language] --> TC[TextTranslationClient]
    TC --> Codes[One or more target codes]
    Codes --> Result[TranslatedTextItem per target]
```

Speech-to-text translation:

```mermaid
flowchart LR
    Mic[Microphone] --> TR[TranslationRecognizer]
    ST[Source language] --> TR
    TR --> Transcript[Source transcript]
    TR --> Dict[translations dictionary]
```

Speech-to-speech translation composes the text translation with speech output:

```mermaid
flowchart LR
    Mic[Spoken source] --> Rec[Speech recognition]
    Rec --> Text[Recognized source text]
    Text --> Translate[Translate to target language]
    Translate --> Target[Translated target text]
    Target --> Synth[Target-language speech synthesis]
    Synth --> Audio[Target audio]
```

Event-based speech output:

```mermaid
flowchart LR
    TR[Single-target TranslationRecognizer] --> Event[Synthesizing event chunks]
    Event --> Bytes[event.result.audio]
    Bytes --> File[Audio output]
```

Manual multi-language speech output:

```mermaid
flowchart LR
    TR[Multi-target TranslationRecognizer] --> Dict[Translations dictionary]
    Dict --> Loop[Loop target languages]
    Loop --> TTS[SpeechSynthesizer + matching voice]
    TTS --> WAV[One audio file per language]
```

The foundry model endpoint, Foundry project endpoint, Speech resource region/endpoint, Translator global endpoint and Voice Agent project's realtime endpoint serve different APIs and must not be substituted for each other.
