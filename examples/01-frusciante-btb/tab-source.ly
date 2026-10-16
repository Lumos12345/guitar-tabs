\version "2.24.3"

\header {
  title = "Before The Beginning"
  subtitle = "John Frusciante"
  composer = "The Empyrean (2009)"
  tagline = ##f
  copyright = "Standard tuning (E A D G B E)  |  Key: Em  |  No capo  |  Notation: eighth notes (positions only)"
}

#(set-global-staff-size 18)

\paper {
  #(set-paper-size "a4")
  top-margin = 18\mm
  bottom-margin = 16\mm
  left-margin = 14\mm
  right-margin = 14\mm
  markup-system-spacing.minimum-distance = #14
  system-system-spacing.minimum-distance = #13
  ragged-last-bottom = ##f
}

%% Standard tuning: 1=high e, 2=B, 3=G, 4=D, 5=A, 6=low E
mytuning = \stringTuning <e, a, d g b e'>   %% low E -> high e  (E A D G B E)

tab = {
  \mark \markup { \vspace #1 \bold \fontsize #2.2 "INTRO / MAIN THEME" }
  % ---- Block 1 ----
    d''8\2^\markup\small\italic "b17" e''8\2 d''8\2^\markup\small\italic "b17" e''8\2 \bar "|" d''8\2 b'8\2 d''8\2 d''8\2 \bar "|" b'8\2 d''8\2 d'8\4 e'8\4 \bar "|" b'8\3^\markup\small\italic "bend" b'8\3^\markup\small\italic "b17" c''8\3 b'8\3 \bar "|"
  \break

  % ---- Block 2 ----
    e''8\2^\markup\small\italic "b19" fis''8\2 e''8\2 d''8\2 \bar "|" d''8\2 b'8\3 e''8\2 d'8\4 \bar "|" e'8\4 b'8\3^\markup\small\italic "vib" d''8\2 b'8\3^\markup\small\italic "b17" \bar "|" c''8\3 b'8\3^\markup\small\italic "vib" \bar "|"
  \break

  % ---- Block 3 ----
    e''8\2^\markup\small\italic "b19" fis''8\2 e''8\2 d''8\2 \bar "|" b''8\1^\markup\small\italic "vib" d''8\2 e''8\2^\markup\small\italic "vib" b''8\1^\markup\small\italic "b20" \bar "|" c'''8\1 b''8\1^\markup\small\italic "b20" c'''8\1 b''8\1^\markup\small\italic "vib" \bar "|"
  \break

  % ---- Block 4 ----
    a''8\1^\markup\small\italic "b19" b''8\1 a''8\1 g''8\1 \bar "|" a''8\1 a''8\1 g''8\1^\markup\small\italic "vib" a''8\1 \bar "|" d''8\2 e''8\2^\markup\small\italic "vib" cis'''8\1^\markup\small\italic "b23" dis'''8\1 \bar "|" c'''8\1 b''8\1 \bar "|"
  \break

  \mark \markup { \vspace #1 \bold \fontsize #2.2 "INTERLUDE" }
  % ---- Block 5 ----
    d'8\3^\markup\small\italic "h9" e'8\3^\markup\small\italic "vib" d'8\3^\markup\small\italic "vib" d'8\3 \bar "|" cis'8\3 c'8\3 g8\4 b8\3^\markup\small\italic "bend vib" \bar "|" g8\4^\markup\small\italic "vib" g8\4^\markup\small\italic "vib" \bar "|"
  \break

  \mark \markup { \vspace #1 \bold \fontsize #2.2 "THEME REPRISE" }
  % ---- Block 6 ----
    d''8\2^\markup\small\italic "b17" e''8\2 d''8\2^\markup\small\italic "b17" e''8\2 \bar "|" d''8\2 b'8\2 d''8\2 d''8\2 \bar "|" b'8\2 d''8\2 d'8\4 e'8\4 \bar "|" b'8\3^\markup\small\italic "b17" c''8\3 b'8\3 g'8\4 \bar "|" b'8\3^\markup\small\italic "b17" c''8\3 b'8\3 g'8\4^\markup\small\italic "vib" \bar "|"
  \break

  % ---- Block 7 ----
    fis'8\4 a'8\4 g'8\4^\markup\small\italic "vib" a'8\4^\markup\small\italic "b20" \bar "|" ais'8\4 a'8\4 d'8\4 e'8\4^\markup\small\italic "vib" \bar "|" b'8\3^\markup\small\italic "b1716" c''8\3 b'8\3 d'8\5^\markup\small\italic "slide" \bar "|" e'8\3^\markup\small\italic "~" b8\4^\markup\small\italic "~" e8\5^\markup\small\italic "~" e,8\6^\markup\small\italic "~" \bar "|"
  \break

  % ---- Block 8 ----
    a8\4^\markup\small\italic "b8" ais8\4 a8\4 g8\4^\markup\small\italic "vib" \bar "|" d'8\3 cis'8\3 c'8\3 e'8\3^\markup\small\italic "vib" \bar "|" b'8\3^\markup\small\italic "vib" b'8\3 d''8\2 a,8\6 \bar "|" e''8\2 \bar "|"
  \break

  % ---- Block 9 ----
    e''8\2^\markup\small\italic "b19" fis''8\2 e''8\2 d''8\2 \bar "|" d''8\2^\markup\small\italic "b17" e''8\2 d''8\2 b'8\3 \bar "|" b'8\3^\markup\small\italic "vib" d''8\2 cis''8\2 c''8\2 \bar "|" b'8\3^\markup\small\italic "b17" c''8\3 b'8\3 g'8\3 \bar "|" b'8\3^\markup\small\italic "b17" c''8\3 b'8\3 g'8\3^\markup\small\italic "vib" \bar "|"
  \break

  % ---- Block 10 ----
    fis'8\3^\markup\small\italic "vib" a'8\3 g'8\3^\markup\small\italic "vib" d'8\4 \bar "|" e'8\4 b'8\2^\markup\small\italic "^" d'8\4^\markup\small\italic "h14" e'8\4^\markup\small\italic "vib" \bar "|" d'8\4^\markup\small\italic "h14" e'8\4 e'8\4 fis'8\3^\markup\small\italic "vib" \bar "|" a'8\3 g'8\3^\markup\small\italic "vib" \bar "|"
  \break

  % ---- Block 11 ----
    a'8\3 d'8\4 e'8\4^\markup\small\italic "vib" d'8\4^\markup\small\italic "h14" \bar "|" e'8\4 d'8\4^\markup\small\italic "/14" e'8\4 d'8\4^\markup\small\italic "h14" \bar "|" e'8\4 d'8\4^\markup\small\italic "/14" e'8\4 d'8\4^\markup\small\italic "h14" \bar "|" e'8\4 d'8\4^\markup\small\italic "/14" e'8\4 d'8\4^\markup\small\italic "h14" \bar "|" e'8\4 g'8\3 e'8\4^\markup\small\italic "vib" \bar "|"
  \break

  % ---- Block 12 ----
    a''8\1^\markup\small\italic "b19" b''8\1 a''8\1 g''8\1 \bar "|" a''8\1 a''8\1 g''8\1^\markup\small\italic "vib" a''8\1 \bar "|" d''8\2 e''8\2^\markup\small\italic "vib" d''8\2^\markup\small\italic "h17" e''8\2 \bar "|" d''8\2 b'8\3 d''8\2 b'8\3 \bar "|"
  \break

  % ---- Block 13 ----
    a'8\3^\markup\small\italic "h16" b'8\3 a'8\3^\markup\small\italic "h16" b'8\3 \bar "|" a'8\3^\markup\small\italic "h16" b'8\3 a'8\3^\markup\small\italic "h16" b'8\3 \bar "|" a'8\3^\markup\small\italic "^" g'8\3^\markup\small\italic "vib" a'8\3 d'8\4 \bar "|" e'8\4 e'8\4^\markup\small\italic "~" e'8\4^\markup\small\italic "~" e'8\4^\markup\small\italic "~" \bar "|" e'8\4^\markup\small\italic "~" \bar "|"
  \break

  % ---- Block 14 ----
    e'8\4^\markup\small\italic "b15" f'8\4^\markup\small\italic "/19" a'8\4 g'8\4^\markup\small\italic "vib" \bar "|" a'8\4^\markup\small\italic "^" d'8\5 e'8\5 b'8\3^\markup\small\italic "b17" \bar "|" c''8\3^\markup\small\italic "h" b'8\3^\markup\small\italic "vib" e''8\2^\markup\small\italic "b19" fis''8\2 \bar "|" e''8\2 d''8\2 e''8\2 d''8\2 \bar "|" b'8\3 \bar "|"
  \break

  % ---- Block 15 ----
    d''8\2 cis''8\2 c''8\2 c''8\2 \bar "|" b'8\3^\markup\small\italic "^" d8\5^\markup\small\italic "h7" e8\5^\markup\small\italic "vib" d8\5^\markup\small\italic "h7" \bar "|" e8\5 d8\5^\markup\small\italic "h7" e8\5 d8\5^\markup\small\italic "h7" \bar "|" e8\5 d8\5^\markup\small\italic "h7" e8\5 fis8\5 \bar "|" a8\4 g8\4^\markup\small\italic "vib" d8\5 e8\5 \bar "|"
  \break

  % ---- Block 16 ----
    b8\4^\markup\small\italic "b10" c'8\4 b8\4^\markup\small\italic "vib" d'8\3^\markup\small\italic "h9" \bar "|" e'8\3 b'8\2 e''8\1 d''8\2 \bar "|" e''8\1 b''8\1^\markup\small\italic "vib" a''8\1^\markup\small\italic "b19" b''8\1 \bar "|" a''8\1 g''8\1^\markup\small\italic "vib" g''8\1 a''8\1 \bar "|" d''8\2 e''8\2 \bar "|"
  \break

  \mark \markup { \vspace #1 \bold \fontsize #2.2 "CLIMAX" }
  % ---- Block 17 ----
    c'''8\1^\markup\small\italic "vib" c'''8\1^\markup\small\italic "b22" d'''8\1 c'''8\1 \bar "|" b''8\1 b''8\1 cis'''8\1^\markup\small\italic "b24" e'''8\1 \bar "|" cis'''8\1^\markup\small\italic "b24" e'''8\1 cis'''8\1 c'''8\1 \bar "|" cis'''8\1^\markup\small\italic "b22" d'''8\1 cis'''8\1 b''8\1 \bar "|" b''8\1^\markup\small\italic "b20" c'''8\1 \bar "|"
  \break

  % ---- Block 18 ----
    e''8\2 d''8\2 e''8\2 d''8\2 \bar "|" e''8\2 e''8\2^\markup\small\italic "~" e''8\2 e''8\2 \bar "|" e''8\2 e''8\2 e''8\2 d''8\2^\markup\small\italic "vib" \bar "|" d''8\2^\markup\small\italic "bend" \bar "|"
  \break

  % ---- Block 19 ----
    ais'8\3 a'8\3^\markup\small\italic "p12" g'8\3 b'8\2 \bar "|" a'8\3^\markup\small\italic "p12" g'8\3 d''8\2^\markup\small\italic "b17" e''8\2 \bar "|" d''8\2 b'8\2 d''8\2 b'8\2 \bar "|" d''8\2 d'8\4 e'8\4 d''8\2^\markup\small\italic "b17" \bar "|" e''8\2 d''8\2 b'8\2 d''8\2 \bar "|" b'8\2 \bar "|"
  \break

  % ---- Block 20 ----
    fis''8\2^\markup\small\italic "vib" d''8\2 d''8\2^\markup\small\italic "h17" e''8\2 \bar "|" d''8\2 d''8\2 cis''8\2 c''8\2 \bar "|" b'8\2^\markup\small\italic "h13" c''8\2 d'8\4^\markup\small\italic "h14" e'8\4 \bar "|"
  \break

  \mark \markup { \vspace #1 \bold \fontsize #2.2 "OUTRO" }
  % ---- Block 21 ----
    e'8\4^\markup\small\italic "vib" fis'8\4 a'8\3 a'8\3^\markup\small\italic "b15" \bar "|" ais'8\3 a'8\3 g'8\3 g'8\3 \bar "|" a'8\3 d'8\4 e'8\4 b'8\2^\markup\small\italic "b13" \bar "|" c''8\2 b'8\2 d'8\4^\markup\small\italic "h14" e'8\4 \bar "|"
  \break

  % ---- Block 22 ----
    e'8\4^\markup\small\italic "vib" fis'8\4 a'8\3 a'8\3^\markup\small\italic "b15" \bar "|" ais'8\3 a'8\3 g'8\3 g'8\3 \bar "|" d''8\2 cis''8\2 c''8\2 e''8\2 \bar "|" d''8\2 e''8\2 e''8\2 d''8\2 \bar "|" e''8\2 \bar "|"
  \break

  % ---- Block 23 ----
    d''8\2 e''8\2 e''8\2 e''8\2^\markup\small\italic "b19" \bar "|" fis''8\2 a''8\1^\markup\small\italic "bend" g''8\1^\markup\small\italic "vib" g''8\1^\markup\small\italic "^" \bar "|" d''8\2 e''8\2 b''8\1^\markup\small\italic "b20" c'''8\1^\markup\small\italic "slide" \bar "|" b8\4^\markup\small\italic "~" e8\5^\markup\small\italic "~" e'8\3^\markup\small\italic "~" \bar "|"
  \break

  % ---- Block 24 ----
    d8\5^\markup\small\italic "h7" e8\5^\markup\small\italic "vib" d8\4 e'8\4^\markup\small\italic "bend" \bar "|" a'8\3^\markup\small\italic "b15" ais'8\3 g'8\3 e'8\4^\markup\small\italic "vib" \bar "|"
  \break

}

\score {
  \new TabStaff \with {
    stringTunings = \mytuning
    \omit Stem
    \omit Flag
    \omit Beam
  } {
    \clef "tab"
    \tabFullNotation
    \override Score.RehearsalMark.self-alignment-X = #LEFT
    \tab
  }
  \layout { }
}
