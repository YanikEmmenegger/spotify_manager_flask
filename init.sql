-- init.sql

CREATE TABLE public.users (
    uuid UUID DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    spotify_uuid VARCHAR(100) UNIQUE,
    name VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL,
    spotify_key TEXT NOT NULL
);

CREATE TABLE public.artists (
    aid VARCHAR(100) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image TEXT,
    complete BOOLEAN DEFAULT false NOT NULL
);

CREATE TABLE public.tracks (
    tid VARCHAR(100) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL REFERENCES public.artists ON UPDATE CASCADE ON DELETE CASCADE,
    image VARCHAR,
    complete BOOLEAN DEFAULT false NOT NULL
);

CREATE TABLE public.recent (
    tid VARCHAR(100) NOT NULL REFERENCES public.tracks ON UPDATE CASCADE ON DELETE CASCADE,
    played_at TIMESTAMP NOT NULL,
    uid VARCHAR(100) NOT NULL REFERENCES public.users (spotify_uuid) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (tid, played_at, uid)
);

CREATE INDEX recent_played_at_uid_idx ON public.recent (played_at, uid);

CREATE TABLE public.genres (
    gid BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);

CREATE TABLE public.artist_genre (
    aid VARCHAR NOT NULL REFERENCES public.artists ON UPDATE CASCADE ON DELETE CASCADE,
    gid BIGINT NOT NULL REFERENCES public.genres ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (aid, gid)
);