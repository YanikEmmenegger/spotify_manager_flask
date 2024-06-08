create table users
(
    uuid         uuid default gen_random_uuid() not null
        constraint user_pkey
            primary key,
    spotify_uuid varchar(100)
        constraint user_spotify_uuid_key
            unique,
    name         varchar(255)                   not null,
    active       boolean                        not null,
    spotify_key  text                           not null
);

alter table users
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on users to anon;

grant delete, insert, references, select, trigger, truncate, update on users to authenticated;

grant delete, insert, references, select, trigger, truncate, update on users to service_role;

create table artists
(
    aid      varchar(100)          not null
        constraint artist_pkey
            primary key,
    name     varchar(255)          not null,
    image    text,
    complete boolean default false not null
);

alter table artists
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on artists to anon;

grant delete, insert, references, select, trigger, truncate, update on artists to authenticated;

grant delete, insert, references, select, trigger, truncate, update on artists to service_role;

create table tracks
(
    tid              varchar(100)          not null
        primary key,
    name             varchar(255)          not null,
    artist           varchar(255)          not null
        references artists
            on update cascade on delete cascade,
    image            varchar,
    complete         boolean default false not null,
    acousticness     real,
    danceability     real,
    energy           real,
    instrumentalness real,
    key              smallint,
    liveness         real,
    loudness         real,
    mode             smallint,
    speechiness      real,
    tempo            real,
    valence          real
);

alter table tracks
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on tracks to anon;

grant delete, insert, references, select, trigger, truncate, update on tracks to authenticated;

grant delete, insert, references, select, trigger, truncate, update on tracks to service_role;

create table recent
(
    tid       varchar(100) not null
        references tracks
            on update cascade on delete cascade,
    played_at timestamp    not null,
    uid       varchar(100) not null
        references users (spotify_uuid)
            on update cascade on delete cascade,
    primary key (tid, played_at, uid)
);

alter table recent
    owner to postgres;

create index recent_played_at_uid_idx
    on recent (played_at, uid);

grant delete, insert, references, select, trigger, truncate, update on recent to anon;

grant delete, insert, references, select, trigger, truncate, update on recent to authenticated;

grant delete, insert, references, select, trigger, truncate, update on recent to service_role;

create table genres
(
    gid  bigint generated by default as identity
        primary key,
    name varchar not null
        unique
);

alter table genres
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on genres to anon;

grant delete, insert, references, select, trigger, truncate, update on genres to authenticated;

grant delete, insert, references, select, trigger, truncate, update on genres to service_role;

create table artist_genre
(
    aid varchar not null
        references artists
            on update cascade on delete cascade,
    gid bigint  not null
        references genres
            on update cascade on delete cascade,
    primary key (aid, gid)
);

alter table artist_genre
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on artist_genre to anon;

grant delete, insert, references, select, trigger, truncate, update on artist_genre to authenticated;

grant delete, insert, references, select, trigger, truncate, update on artist_genre to service_role;

create table playlists
(
    pid          serial
        primary key,
    spotify_uuid varchar(255) not null,
    name         varchar(255) not null,
    created_at   timestamp default CURRENT_TIMESTAMP
);

alter table playlists
    owner to postgres;

grant select, update, usage on sequence playlists_pid_seq to anon;

grant select, update, usage on sequence playlists_pid_seq to authenticated;

grant select, update, usage on sequence playlists_pid_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on playlists to anon;

grant delete, insert, references, select, trigger, truncate, update on playlists to authenticated;

grant delete, insert, references, select, trigger, truncate, update on playlists to service_role;

create table playlist_genre
(
    pid integer not null
        references playlists,
    gid integer not null
        references genres,
    primary key (pid, gid)
);

alter table playlist_genre
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on playlist_genre to anon;

grant delete, insert, references, select, trigger, truncate, update on playlist_genre to authenticated;

grant delete, insert, references, select, trigger, truncate, update on playlist_genre to service_role;

create table playlist_exceptions
(
    pid   integer      not null
        references playlists,
    type  varchar(10)  not null
        constraint playlist_exceptions_type_check
            check ((type)::text = ANY ((ARRAY ['artist'::character varying, 'track'::character varying])::text[])),
    value varchar(255) not null,
    primary key (pid, type, value)
);

alter table playlist_exceptions
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on playlist_exceptions to anon;

grant delete, insert, references, select, trigger, truncate, update on playlist_exceptions to authenticated;

grant delete, insert, references, select, trigger, truncate, update on playlist_exceptions to service_role;

create table topmix_exception
(
    spotify_uuid varchar(255) not null,
    type         varchar(10)  not null
        constraint topmix_exception_type_check
            check ((type)::text = ANY ((ARRAY ['artist'::character varying, 'track'::character varying])::text[])),
    value        varchar(255) not null,
    primary key (spotify_uuid, type, value)
);

alter table topmix_exception
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on topmix_exception to anon;

grant delete, insert, references, select, trigger, truncate, update on topmix_exception to authenticated;

grant delete, insert, references, select, trigger, truncate, update on topmix_exception to service_role;

