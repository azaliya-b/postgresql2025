DROP TABLE IF EXISTS posts, users, tags, votes, comments CASCADE;

-- ===========================
-- Таблица: Users
-- ===========================
CREATE TABLE Users (
    Id INTEGER PRIMARY KEY,
    AccountId INTEGER,
    Reputation INTEGER,
    CreationDate TIMESTAMP,
    DisplayName TEXT,
    LastAccessDate TIMESTAMP,
    WebsiteUrl TEXT,
    Location TEXT,
    AboutMe TEXT,
    Views INTEGER,
    UpVotes INTEGER,
    DownVotes INTEGER
);

-- ===========================
-- Таблица: Posts
-- ===========================
CREATE TABLE Posts (
    Id INTEGER PRIMARY KEY,
    PostTypeId SMALLINT,
    ParentId INTEGER,
    AcceptedAnswerId INTEGER,
    CreationDate TIMESTAMP,
    Score INTEGER,
    ViewCount INTEGER,
    Body TEXT,
    OwnerUserId INTEGER,
    LastEditorUserId INTEGER,
    LastEditDate TIMESTAMP,
    LastActivityDate TIMESTAMP,
    Title TEXT,
    Tags TEXT,
    AnswerCount INTEGER,
    CommentCount INTEGER,
    FavoriteCount INTEGER,
    ClosedDate TIMESTAMP,
    CommunityOwnedDate TIMESTAMP,
    ContentLicense TEXT
);

-- ===========================
-- Таблица: Tags
-- ===========================
CREATE TABLE Tags (
    Id INTEGER PRIMARY KEY,
    TagName TEXT,
    Count INTEGER,
    ExcerptPostId INTEGER,
    WikiPostId INTEGER,
    IsModeratorOnly BOOLEAN,
    IsRequired BOOLEAN
);

-- ===========================
-- Таблица: Votes
-- ===========================
CREATE TABLE Votes (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER,
    VoteTypeId SMALLINT,
    CreationDate TIMESTAMP
);

-- ===========================
-- Таблица: Badges
-- ===========================
CREATE TABLE Badges (
    Id INTEGER PRIMARY KEY,
    UserId INTEGER,
    Name TEXT,
    Date TIMESTAMP,
    Class SMALLINT,
    TagBased BOOLEAN
);

-- ===========================
-- Таблица: PostHistory
-- ===========================
CREATE TABLE PostHistory (
    Id INTEGER PRIMARY KEY,
    PostHistoryTypeId SMALLINT,
    PostId INTEGER,
    RevisionGUID UUID,
    CreationDate TIMESTAMP,
    UserId INTEGER,
    Comment TEXT,
    Text TEXT,
    ContentLicense TEXT
);

-- ===========================
-- Таблица: PostLinks
-- ===========================
CREATE TABLE PostLinks (
    Id INTEGER PRIMARY KEY,
    CreationDate TIMESTAMP,
    PostId INTEGER,
    RelatedPostId INTEGER,
    LinkTypeId SMALLINT
);

-- ===========================
-- Таблица: Comments
-- ===========================
CREATE TABLE Comments (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER,
    Score INTEGER,
    Text VARCHAR,
    CreationDate TIMESTAMP,
    UserId INTEGER
);

