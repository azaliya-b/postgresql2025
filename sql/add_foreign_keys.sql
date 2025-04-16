-- ===========================
-- Внешние ключи
-- ===========================
ALTER TABLE Posts
    ADD FOREIGN KEY (OwnerUserId) REFERENCES Users(Id),
    ADD FOREIGN KEY (LastEditorUserId) REFERENCES Users(Id),
    ADD FOREIGN KEY (ParentId) REFERENCES Posts(Id),
    ADD FOREIGN KEY (AcceptedAnswerId) REFERENCES Posts(Id);

ALTER TABLE Tags
    ADD FOREIGN KEY (ExcerptPostId) REFERENCES Posts(Id),
    ADD FOREIGN KEY (WikiPostId) REFERENCES Posts(Id);

ALTER TABLE Votes
    ADD FOREIGN KEY (PostId) REFERENCES Posts(Id);

ALTER TABLE Badges
    ADD FOREIGN KEY (UserId) REFERENCES Users(Id);

ALTER TABLE PostHistory
    ADD FOREIGN KEY (PostId) REFERENCES Posts(Id),
    ADD FOREIGN KEY (UserId) REFERENCES Users(Id);

ALTER TABLE PostLinks
    ADD FOREIGN KEY (PostId) REFERENCES Posts(Id),
    ADD FOREIGN KEY (RelatedPostId) REFERENCES Posts(Id);

ALTER TABLE Comments
    ADD FOREIGN KEY (PostId) REFERENCES Posts(Id),
    ADD FOREIGN KEY (UserId) REFERENCES Users(Id);