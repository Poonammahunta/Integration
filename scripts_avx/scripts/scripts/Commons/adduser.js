db.createUser({
"user":"admin",
"pwd":"admin",
"roles":[{role:'__system', db : 'admin'}]
});
db.createUser({
"user":"appviewx",
"pwd":"appviewx",
"roles":[{role:'__system', db : 'admin'}]
});
db.createUser({
"user":"aps",
"pwd":"aps@123",
"roles":[{role:'read', db : 'appviewx'}, {role:'read', db : 'workFlowDBEngine'}]
});
db.revokeRolesFromUser('aps',[{role:'root', db:'admin'}]);


