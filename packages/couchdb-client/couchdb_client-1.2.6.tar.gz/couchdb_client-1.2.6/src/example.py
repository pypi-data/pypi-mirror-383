import couchdb_client

db = couchdb_client.CouchDB('admin', 'admin', 't')

with open('/tmp/out', 'wb') as f:
    f.write(db.get_all_documents()[0].attachments[0].data)


exit()

# create a document instance
doc = db.document({
    'key_test': 'value test'
})
doc.create()  # create the document in the database

print(db.get_document(doc.id))  # get the document
# note: doc.id is the same as doc['_id']

# update the document
doc['key_test'] = 'test blabla'
doc.update()

# get the document again to the the updated data
print(db.get_document(doc.id))

# delete the document
doc.delete()

print(db.get_document(doc.id))  # should return none since the document was deleted

# insert multiple documents at once
inserted = db.create_documents([
    db.document({'test1': 1}),
    db.document({'test1': 2}),
    db.document({'test1': 3}),
    db.document({'test1': 4})
])
print(inserted)

# should return the last two documents just above
print(db.find_documents({
    'test1': {
        '$gt': 2
    }
}))

for doc in inserted:  # delete them
    doc.delete()

print(db.find_documents({  # should be empty
    'test1': {
        '$gt': 2
    }
}))

print(db.get_all_documents(skip=100, limit=10))  # get 10 documents, starting from the 100th
