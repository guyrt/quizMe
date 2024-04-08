Customer Models are data models owned by a customer. Wezo's job is to map data into that format. 

We want to support a few patterns:

1. I have a table. Insert new rows.
1. I have tables with an FK relationship. I need to add a row to child that maps to parent.
1. I have a table and a row. Modify the row (but keep in mind everything is immutable)


This app contains a few parts:

1. Rudimentary system for collecting new schemas in markdown.
2. Internal data models for customer data
3. Matching logic

Types of data I need to long term manage:

1. Calendar + meetings. You can do a mix of direct matching with invite info plus the content.
2. Docs. Can be about an entity
3. Emails/chats *with* and *about*
4. Random internet stuff



