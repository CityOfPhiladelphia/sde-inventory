# tests

_TODO_: write tests :)

## `get_changes`

There are two snapshots in the `fixtures` folder:

- `inventory.json`
- `inventory2.json`

that are good for testing the `get_changes` command -- they produce one change per change type.

### Expected Changes

```
--------------------------------------------------------------------------------
CHANGE TYPE          |  OBJECT NAME
--------------------------------------------------------------------------------

ADD_USER                USER_TO_ADD                   
  ADD_TABLE             USER_TO_ADD_TABLE             
  ADD_INDEX             USER_TO_ADD_INDEX             
  ADD_PRIVILEGE         USER_TO_ADD_PRIVILEGE         
REMOVE_USER             USER_TO_REMOVE                

ADD_TABLE               TABLE_TO_ADD                  
  ADD_INDEX             TABLE_TO_ADD_INDEX            
  ADD_PRIVILEGE         TABLE_TO_ADD_PRIVILEGE        
REMOVE_TABLE            TABLE_TO_REMOVE                     

ADD_PRIVILEGE           PRIVILEGE_TO_ADD              
REMOVE_PRIVILEGE        PRIVILEGE_TO_REMOVE           

ADD_INDEX               INDEX_TO_ADD   
REMOVE_INDEX            INDEX_TO_REMOVE
update: this should generate an add/remove:
ADD_INDEX               INDEX_TO_UPDATE
REMOVE_INDEX            INDEX_TO_UPDATE

ADD_FIELD               FIELD_TO_ADD   
REMOVE_FIELD            FIELD_TO_REMOVE
update: this should generate an add/remove:
ADD_FIELD               FIELD_TO_UPDATE
REMOVE_FIELD            FIELD_TO_UPDATE

```
