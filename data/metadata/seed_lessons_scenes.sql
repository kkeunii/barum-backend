CREATE TABLE IF NOT EXISTS lessons (
    lessons_id BIGINT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'easy',
    thumbnail_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scenes (
    scenes_id BIGSERIAL PRIMARY KEY,
    lesson_id BIGINT NOT NULL REFERENCES lessons(lessons_id),
    order_index INTEGER NOT NULL,
    sentence TEXT NOT NULL,
    video_url TEXT NOT NULL,
    audio_url TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE scenes
ADD COLUMN IF NOT EXISTS audio_url TEXT NOT NULL DEFAULT '';

INSERT INTO lessons (
    lessons_id,
    title,
    description,
    difficulty,
    thumbnail_url,
    is_active
) VALUES
    (
        1,
        '레슨1',
        '비행기에서, 리허설중에, 국밥집에서 표현 연습',
        'medium',
        NULL,
        true
    ),
    (
        2,
        '레슨2',
        '한의원에서, 사자보이즈등장, 예능촬영 표현 연습',
        'medium',
        NULL,
        true
    ),
    (
        3,
        '레슨3',
        '진우와대화, 미라와대화, 헌트릭스대화 표현 연습',
        'easy',
        NULL,
        true
    )
ON CONFLICT (lessons_id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    difficulty = EXCLUDED.difficulty,
    thumbnail_url = EXCLUDED.thumbnail_url,
    is_active = EXCLUDED.is_active,
    updated_at = now();

INSERT INTO scenes (
    scenes_id,
    lesson_id,
    order_index,
    sentence,
    video_url,
    audio_url,
    is_active
) VALUES
    (
        1,
        1,
        1,
        '우리 지금 라면 먹으려고',
        '/clips/clip_001.mp4',
        '/reference-audio/U001_reference.mp3',
        true
    ),
    (
        2,
        1,
        2,
        '잠깐 끊죠. 5분만 쉴게요.',
        '/clips/clip_002.mp4',
        '/reference-audio/U002_reference.mp3',
        true
    ),
    (
        3,
        1,
        3,
        '나, 그게 가능할지 잘 모르겠어.',
        '/clips/clip_003.mp4',
        '/reference-audio/U003_reference.mp3',
        true
    ),
    (
        4,
        2,
        1,
        '저흰 약만 받으러 온거에요.',
        '/clips/clip_004.mp4',
        '/reference-audio/U004_reference.mp3',
        true
    ),
    (
        5,
        2,
        2,
        '안돼, 사람이 많아.',
        '/clips/clip_005.mp4',
        '/reference-audio/U005_reference.mp3',
        true
    ),
    (
        6,
        2,
        3,
        '저희야 말로 영광이죠.',
        '/clips/clip_006.mp4',
        '/reference-audio/U006_reference.mp3',
        true
    ),
    (
        7,
        3,
        1,
        '난 너하곤 달라.',
        '/clips/clip_007.mp4',
        '/reference-audio/U007_reference.mp3',
        true
    ),
    (
        8,
        3,
        2,
        '너한테 숨기는거 없어.',
        '/clips/clip_008.mp4',
        '/reference-audio/U008_reference.mp3',
        true
    ),
    (
        9,
        3,
        3,
        '지금 컨디션 최고야.',
        '/clips/clip_009.mp4',
        '/reference-audio/U009_reference.mp3',
        true
    )
ON CONFLICT (scenes_id) DO UPDATE SET
    lesson_id = EXCLUDED.lesson_id,
    order_index = EXCLUDED.order_index,
    sentence = EXCLUDED.sentence,
    video_url = EXCLUDED.video_url,
    audio_url = EXCLUDED.audio_url,
    is_active = EXCLUDED.is_active,
    updated_at = now();

SELECT setval(
    pg_get_serial_sequence('scenes', 'scenes_id'),
    COALESCE((SELECT MAX(scenes_id) FROM scenes), 1)
);
