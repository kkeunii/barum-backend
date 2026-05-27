import math
import subprocess
import wave
from array import array
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional, Tuple


TARGET_SAMPLE_RATE = 16000
FRAME_SIZE = 480
HOP_SIZE = 160
MIN_PITCH_HZ = 80
MAX_PITCH_HZ = 400
MIN_RMS = 500.0
ENDING_FRAME_COUNT = 5
REFERENCE_AUDIO_DIR = Path("data/audio/reference")
REFERENCE_AUDIO_MAP: dict[str, Path] = {}


def _decode_to_wav(source_path: Path, output_path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-ac",
            "1",
            "-ar",
            str(TARGET_SAMPLE_RATE),
            "-f",
            "wav",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def resolve_reference_audio(
    expected_text: str,
    uploaded_reference_audio_path: Optional[Path] = None,
) -> Tuple[Optional[Path], Optional[str]]:
    if uploaded_reference_audio_path is not None:
        if uploaded_reference_audio_path.exists():
            return uploaded_reference_audio_path, None
        return None, "reference audio upload was provided but could not be saved"

    reference_audio_path = REFERENCE_AUDIO_MAP.get(expected_text.strip())
    if reference_audio_path is None:
        return None, "no reference audio mapping found for expected_text in data/audio/reference"

    if not reference_audio_path.exists():
        return None, "mapped reference audio file is missing in data/audio/reference"

    return reference_audio_path, None


def _load_wav_samples(audio_path: Path) -> Tuple[int, List[int]]:
    with wave.open(str(audio_path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())

    samples = array("h")
    samples.frombytes(frames)
    return sample_rate, samples.tolist()


def _calculate_rms(frame: List[int]) -> float:
    if not frame:
        return 0.0

    square_sum = 0.0
    for sample in frame:
        square_sum += float(sample * sample)

    return math.sqrt(square_sum / len(frame))


def _estimate_pitch(frame: List[int], sample_rate: int) -> Optional[float]:
    if len(frame) < FRAME_SIZE or _calculate_rms(frame) < MIN_RMS:
        return None

    min_lag = max(1, int(sample_rate / MAX_PITCH_HZ))
    max_lag = max(min_lag, int(sample_rate / MIN_PITCH_HZ))

    best_lag = 0
    best_score = 0.0

    for lag in range(min_lag, max_lag + 1):
        score = 0.0
        for index in range(len(frame) - lag):
            score += frame[index] * frame[index + lag]

        if score > best_score:
            best_score = score
            best_lag = lag

    if best_lag == 0:
        return None

    return round(sample_rate / best_lag, 2)


def _extract_pitch_contour(samples: List[int], sample_rate: int) -> List[float]:
    pitches: List[float] = []

    for start in range(0, max(0, len(samples) - FRAME_SIZE + 1), HOP_SIZE):
        frame = samples[start : start + FRAME_SIZE]
        pitch = _estimate_pitch(frame, sample_rate)
        if pitch is not None:
            pitches.append(pitch)

    return pitches


def _calculate_average(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def _calculate_ending_slope(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None

    ending_values = values[-ENDING_FRAME_COUNT:]
    if len(ending_values) < 2:
        return None

    return (ending_values[-1] - ending_values[0]) / (len(ending_values) - 1)


def _calculate_pitch_similarity(
    reference_pitches: List[float], uploaded_pitches: List[float]
) -> Optional[float]:
    reference_average = _calculate_average(reference_pitches)
    uploaded_average = _calculate_average(uploaded_pitches)

    if reference_average is None or uploaded_average is None or reference_average <= 0:
        return None

    difference_ratio = abs(reference_average - uploaded_average) / reference_average
    similarity = max(0.0, 100.0 - (difference_ratio * 100.0))
    return round(similarity, 2)


def _calculate_total_frames(samples: List[int]) -> int:
    if len(samples) < FRAME_SIZE:
        return 0

    return 1 + max(0, (len(samples) - FRAME_SIZE) // HOP_SIZE)


def _count_text_units(text: str) -> int:
    return len([char for char in text if not char.isspace()])


def _calculate_speech_rate(expected_text: str, duration_seconds: float) -> Optional[float]:
    if not expected_text or duration_seconds <= 0:
        return None

    unit_count = _count_text_units(expected_text)
    if unit_count == 0:
        return None

    return round(unit_count / duration_seconds, 2)


def _identify_ending_pattern(slope: Optional[float]) -> Optional[str]:
    if slope is None:
        return None

    if slope > 2.0:
        return "rising"
    if slope < -2.0:
        return "falling"

    return "flat"


def _target_prosody_type_to_pattern(target_prosody_type: Optional[str]) -> Optional[str]:
    if not isinstance(target_prosody_type, str):
        return None

    if target_prosody_type == "sentence_final_fall":
        return "falling"

    return None


def _pattern_label(pattern: Optional[str]) -> str:
    if pattern == "rising":
        return "올라가는"
    if pattern == "falling":
        return "내려가는"
    return "평탄한"


def _calculate_rhythm_score(
    pitches: List[float], total_frames: int
) -> Optional[float]:
    if len(pitches) < 2 or total_frames == 0:
        return None

    pitch_deltas = [abs(pitches[i + 1] - pitches[i]) for i in range(len(pitches) - 1)]
    average_delta = _calculate_average(pitch_deltas)
    if average_delta is None or average_delta == 0:
        base_score = 100.0
    else:
        variation = sum(abs(delta - average_delta) for delta in pitch_deltas) / len(
            pitch_deltas
        )
        base_score = max(0.0, 100.0 - (variation / average_delta * 80.0))

    voiced_ratio = len(pitches) / total_frames
    if voiced_ratio < 0.5:
        base_score *= 0.8

    return round(min(100.0, max(0.0, base_score)), 2)


def _calculate_prosody_score(
    pitch_similarity: Optional[float],
    ending_slope_difference: Optional[float],
    rhythm_score: Optional[float],
    duration_ratio: Optional[float],
) -> Optional[float]:
    if pitch_similarity is None or ending_slope_difference is None:
        return None

    score = pitch_similarity
    score -= min(20.0, ending_slope_difference * 2.0)
    if rhythm_score is not None:
        score = score * 0.7 + rhythm_score * 0.3

    if duration_ratio is not None and (duration_ratio < 0.9 or duration_ratio > 1.15):
        score -= 7.0

    return round(max(0.0, min(100.0, score)), 2)


def _build_prosody_feedback(
    pitch_similarity: Optional[float],
    ending_slope_difference: Optional[float],
    expected_pattern: Optional[str],
    ending_pattern: Optional[str],
    speech_rate: Optional[float],
    duration_ratio: Optional[float],
    rhythm_score: Optional[float],
) -> dict[str, object]:
    issues: list[str] = []
    actions: list[str] = []
    focus = "전체 억양"
    severity = "good"

    if duration_ratio is not None:
        if duration_ratio < 0.9:
            issues.append("말이 너무 빨라 억양이 뭉친 느낌이에요.")
            actions.append("조금 느리게 말하며 문장 끝을 또박또박 들어보세요.")
            focus = "말하기 속도"
            severity = "warning"
        elif duration_ratio > 1.15:
            issues.append("말이 너무 느려 문장 흐름이 끊겼어요.")
            actions.append(
                "호흡을 줄이고 자연스럽게 이어서 말해보세요."
            )
            focus = "말하기 속도"
            severity = "warning"

    if rhythm_score is not None and rhythm_score < 60:
        issues.append(
            "리듬이 일정하지 않아 호흡이나 끊김이 느껴집니다."
        )
        actions.append(
            "한 번에 이어 말할 때 숨을 고르되, 너무 자주 끊지 않도록 해보세요."
        )
        focus = "리듬"
        severity = "warning"

    if expected_pattern and ending_pattern:
        if expected_pattern != ending_pattern:
            issues.append(
                f"문장 끝은 {_pattern_label(expected_pattern)} 억양이어야 하는데 {_pattern_label(ending_pattern)} 느낌이에요."
            )
            actions.append(
                f"문장 마지막 음을 {_pattern_label(expected_pattern)} 방향으로 연습해보세요."
            )
            focus = "문장 끝 억양"
            severity = "warning"
        elif pitch_similarity is not None and pitch_similarity < 70:
            issues.append(
                "문장 끝 패턴은 맞았지만 전체 높낮이 흐름이 많이 달라요."
            )
            actions.append(
                "처음부터 끝까지 말할 때 높낮이 변화를 더 자연스럽게 살려보세요."
            )
            focus = "전체 흐름"
            severity = "warning"
        elif pitch_similarity is not None and pitch_similarity < 85:
            issues.append(
                "끝은 괜찮지만 전체 흐름이 조금 단조롭게 들렸어요."
            )
            actions.append(
                "문장 전체를 조금 더 살려 말해보세요."
            )
            focus = "전체 흐름"
            severity = "warning"
    elif pitch_similarity is not None and ending_slope_difference is not None:
        if pitch_similarity >= 80 and ending_slope_difference > 5:
            issues.append(
                "전체 높낮이 흐름은 비슷한데 마지막 부분 억양 방향이 달라요."
            )
            actions.append(
                "끝 부분만 다시 말하면서 문장 마지막 음을 신경 써보세요."
            )
            focus = "문장 끝 억양"
            severity = "warning"
        elif pitch_similarity < 60:
            issues.append(
                "전체 높낮이 흐름이 예상과 많이 달라요."
            )
            actions.append(
                "처음부터 끝까지 원어민 음성을 들으며 높낮이 변화를 따라해보세요."
            )
            focus = "전체 흐름"
            severity = "warning"
        elif pitch_similarity < 80:
            issues.append(
                "전체 흐름은 어느 정도 맞지만 조금 더 자연스럽게 다듬으면 좋아요."
            )
            actions.append(
                "더 자연스럽게 이어 말하는 연습을 해보세요."
            )
            focus = "전체 흐름"
            severity = "warning"

    if not issues:
        issues.append(
            "전체 높낮이 흐름과 문장 끝 패턴이 잘 맞았어요."
        )
        actions.append(
            "이 느낌을 유지하며 다음 문장도 연습해보세요."
        )
        focus = "전체 억양"
        severity = "good"

    headline = issues[0]
    reason = " ".join(issues)
    action = " ".join(actions)

    return {
        "headline": headline,
        "reason": reason,
        "action": action,
        "focus": focus,
        "severity": severity,
    }


def score_prosody(
    reference_audio_path: Optional[Path],
    uploaded_audio_path: Path,
    expected_text: Optional[str] = None,
    target_prosody_type: Optional[str] = None,
) -> dict[str, object]:
    if reference_audio_path is None:
        return {
            "pitch_similarity": None,
            "ending_slope_difference": None,
            "speech_rate": None,
            "rhythm_score": None,            "prosody_score": None,            "ending_pattern_match": None,
            "ending_pattern": None,
            "expected_pattern": None,
            "target_prosody_type": target_prosody_type,
            "prosody_feedback": {
                "headline": "참고 음성이 없어 억양을 판단하기 어려워요.",
                "reason": "reference audio is missing",
                "action": "녹음 대상 문장에 대한 참고 음성을 준비해주세요.",
                "focus": "문장 끝 억양",
                "severity": "warning",
            },
            "reason": "reference audio is missing",
        }

    try:
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            reference_wav_path = temp_dir_path / "reference.wav"
            uploaded_wav_path = temp_dir_path / "uploaded.wav"

            _decode_to_wav(reference_audio_path, reference_wav_path)
            _decode_to_wav(uploaded_audio_path, uploaded_wav_path)

            reference_sample_rate, reference_samples = _load_wav_samples(reference_wav_path)
            uploaded_sample_rate, uploaded_samples = _load_wav_samples(uploaded_wav_path)

            reference_pitches = _extract_pitch_contour(
                reference_samples, reference_sample_rate
            )
            uploaded_pitches = _extract_pitch_contour(
                uploaded_samples, uploaded_sample_rate
            )
            reference_frames = _calculate_total_frames(reference_samples)
            uploaded_frames = _calculate_total_frames(uploaded_samples)
            reference_duration = len(reference_samples) / reference_sample_rate
            uploaded_duration = len(uploaded_samples) / uploaded_sample_rate
    except (OSError, subprocess.SubprocessError, wave.Error):
        return {
            "pitch_similarity": None,
            "ending_slope_difference": None,
            "speech_rate": None,
            "rhythm_score": None,            "prosody_score": None,            "ending_pattern_match": None,
            "ending_pattern": None,
            "expected_pattern": None,
            "target_prosody_type": target_prosody_type,
            "prosody_feedback": {
                "headline": "억양 점수를 계산할 수 없어요.",
                "reason": "failed to decode audio for prosody scoring",
                "action": "오디오 파일이 손상되지 않았는지 확인하고 다시 시도해보세요.",
                "focus": "문장 끝 억양",
                "severity": "warning",
            },
            "reason": "failed to decode audio for prosody scoring",
        }

    pitch_similarity = _calculate_pitch_similarity(
        reference_pitches, uploaded_pitches
    )
    ending_slope_difference = _calculate_ending_slope_difference(
        reference_pitches, uploaded_pitches
    )
    speech_rate = _calculate_speech_rate(expected_text or "", uploaded_duration)
    duration_ratio = None
    if reference_duration > 0:
        duration_ratio = round(uploaded_duration / reference_duration, 2)

    reference_pattern = _target_prosody_type_to_pattern(target_prosody_type)
    if reference_pattern is None:
        reference_pattern = _identify_ending_pattern(
            _calculate_ending_slope(reference_pitches)
        )

    uploaded_pattern = _identify_ending_pattern(
        _calculate_ending_slope(uploaded_pitches)
    )

    ending_pattern_match = None
    if reference_pattern is not None and uploaded_pattern is not None:
        ending_pattern_match = reference_pattern == uploaded_pattern

    rhythm_score = _calculate_rhythm_score(uploaded_pitches, uploaded_frames)
    prosody_score = _calculate_prosody_score(
        pitch_similarity,
        ending_slope_difference,
        rhythm_score,
        duration_ratio,
    )

    reason = None
    if not reference_pitches:
        reason = "reference audio did not contain enough voiced frames"
    elif not uploaded_pitches:
        reason = "uploaded audio did not contain enough voiced frames"
    elif pitch_similarity is None or ending_slope_difference is None:
        reason = "prosody features could not be calculated from the audio"

    prosody_feedback = _build_prosody_feedback(
        pitch_similarity,
        ending_slope_difference,
        reference_pattern,
        uploaded_pattern,
        speech_rate,
        duration_ratio,
        rhythm_score,
    )

    return {
        "pitch_similarity": pitch_similarity,
        "ending_slope_difference": ending_slope_difference,
        "speech_rate": speech_rate,
        "rhythm_score": rhythm_score,
        "prosody_score": prosody_score,
        "ending_pattern_match": ending_pattern_match,
        "ending_pattern": uploaded_pattern,
        "expected_pattern": reference_pattern,
        "target_prosody_type": target_prosody_type,
        "prosody_feedback": prosody_feedback,
        "reason": reason,
    }
