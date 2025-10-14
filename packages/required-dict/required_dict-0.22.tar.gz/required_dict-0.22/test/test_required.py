import pytest 
import fupi
from required_dict import REQUIRED


def should_error(**kwargs):
    if not 'failmsg' in kwargs: failmsg = 'The Validation did not FAIL as expected.' 
    else: 
        failmsg = kwargs['failmsg']
        del kwargs['failmsg']
    try: 
        pytest.raises(ValueError,  REQUIRED.validate_data(**kwargs))
        return failmsg
    except ValueError as e:
        print(f'\n{e}') # returns user-friendly error message 
        return str(e) 

def should_warn(**kwargs):
    if not 'failmsg' in kwargs: failmsg = 'The Validation did not FAIL as expected.' 
    else: 
        failmsg = kwargs['failmsg']
        del kwargs['failmsg']
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        REQUIRED.validate_data(**kwargs)
        if w and len(w) > 0:
            print(f'\n{w[0].message}') # returns user-friendly warning message 
            return str(w[0].message)
        return failmsg 




def test_required():
        
    user_data = {
        'user_name': 'John Doe',
        'user_id': '12345678-1234-7654-8765-123456789012',
        'user_age': 30,
        'user_type': 'buyer',
        'user_email': 'john@example.com',
        'user_detail': '{"some":"thing", "foo":"bar", "baz":123}',
        'joined_time': '2025-10-01T00:00:00+00:00',
    }
    
    validation = {
        'user_name':    REQUIRED(),
        'user_id':      REQUIRED().as_uuid(),
        'user_age':     REQUIRED().greater_than(18),
        'user_balance': REQUIRED().as_posnum().default(0),
        'user_type':    REQUIRED().constrain_to('buyer', 'seller'),
        'user_email':   REQUIRED().as_type(str),
        'user_detail':  REQUIRED().as_json(),
        'joined_time':  REQUIRED().as_isotime(),
        'sel_product':  REQUIRED().default('Cookies'),
        'notes':  'This becomes the default if the key is missing, or value None.'
    }

    # Generates a net-new, validated dictionary:
    valid_data = REQUIRED.validate_data(validation, user_data)
    

    # Any required, non-defaulted keys must exist, or validation will fail:
    err = should_error(
                validation={'id': REQUIRED(), 'user_name': REQUIRED()}, 
                user_data= {'id': 123 }) # missing user_name
    assert 'user_name = REQUIRED - Missing' in err

    # also, values must be Truthy, aka not None or empty (note difference in error message):
    err = should_error(
                validation={'id': REQUIRED(), 'user_name': REQUIRED()}, 
                user_data= {'id': 123, 'user_name': None})
    assert 'user_name = REQUIRED - Present, but Empty' in err

    # you can however make .none_ok():
    assert REQUIRED.validate_data(
                validation={'id': REQUIRED(), 'user_name': REQUIRED().none_ok()}, 
                user_data= {'id': 123, 'user_name': None})

    # the user can of course assign a value to the REQUIRED key, and validation passes:
    assert REQUIRED.validate_data(
                validation={'id': REQUIRED(), 'user_name': REQUIRED().none_ok()}, 
                user_data= {'id': 123, 'user_name': 'susy'})

    # always displays user-friendly error message, including why validation failed,
    # what the value was, and a list of all required and optional keys (full validation signature)
    print(err)

    # you can define fields in validation that are NOT REQUIRED. For example:
    assert REQUIRED.validate_data(
                validation={'id': REQUIRED(), 'user_type':'buyer'}, 
                user_data= {'id': 123})
    
    # since user_type is not REQUIRED, this passes just fine.  If user_data does not contain 
    # a non-REQUIRED key in validation, it's treated as an optional default, and added to the 
    # output of validate_data.  i.e., 
    valid_data = REQUIRED.validate_data(
                    validation={'id': REQUIRED(), 'user_type':'buyer'}, 
                    user_data= {'id': 123})
    assert valid_data['user_type'] == 'buyer'
    
    # this is similar to using a .default(), however you can chain .default() along with other 
    # validations that still apply. i.e., if omitted, default applies:
    assert REQUIRED.validate_data(
                validation={'id': REQUIRED(), 'user_type': REQUIRED().as_type(str).default('buyer')}, 
                user_data= {'id': 123}
                )['user_type'] == 'buyer'
    
    # but if provided, it must pass all other validations:
    err = should_error(
                validation={'id': REQUIRED(), 'user_type': REQUIRED().as_type(str).default('buyer')}, 
                user_data= {'id': 123, 'user_type': 456} )
    assert 'user_type = REQUIRED - Wrong Type (requires str, not int)' in err    
    


 
    # ----------------------------------------
    # numeric validations can check: 
    # is positive or negative:
    err = should_error(
            validation={'balance':REQUIRED().as_posnum()}, 
            user_data= {'balance': -20})
    assert 'balance = REQUIRED - Present, but Not a Positive Number (-20)' in err
 
    err = should_error(
            validation={'balance':REQUIRED().as_negnum()}, 
            user_data= {'balance': 20})
    assert 'balance = REQUIRED - Present, but Not a Negative Number (20)' in err
 
    # or can check whether greater_than or less_than some value:
    err = should_error(
            validation={'user_age':REQUIRED().greater_than(13)}, 
            user_data= {'user_age': 12})
    assert 'user_age = REQUIRED - Present, but Not Greater Than 13 (12)' in err
 
    err = should_error(
            validation={'user_age':REQUIRED().less_than(18)}, 
            user_data= {'user_age': 22})
    assert 'user_age = REQUIRED - Present, but Not Less Than 18 (22)' in err
 
    # by default, these are both exclusive of the value supplied, 
    # i.e., not equal-to:
    err = should_error(
            validation={'user_age':REQUIRED().less_than(18)}, 
            user_data= {'user_age': 18})
    assert 'user_age = REQUIRED - Present, but Not Less Than 18 (18)' in err

    # there is an optional flag that provides the `equal_to` capability:
    assert REQUIRED.validate_data(
            validation={'user_age':REQUIRED().less_than(18, or_equal_to = True)}, 
            user_data= {'user_age': 18})
    assert REQUIRED.validate_data(
            validation={'user_age':REQUIRED().greater_than(13, or_equal_to = True)}, 
            user_data= {'user_age': 13})
    
    # you can chain these together to build a range:
    assert REQUIRED.validate_data(
            validation={'user_age':REQUIRED().greater_than(13, True).less_than(18, True)}, 
            user_data= {'user_age': 16})

    
    # ----------------------------------------
    # Aliases allow you to accept multiple keys for the same value.
    # For example, your user_data may come in with `id` or `user_id` or `party_id`
    # and at least ONE of those are REQUIRED.
    valid_data = REQUIRED.validate_data(
            validation={'id':REQUIRED().alias('user_id', 'party_id').as_type(str) }, 
            user_data= {'user_id': 'a20d3b07c'})
    assert valid_data['id'] == 'a20d3b07c'
    assert valid_data['user_id'] == 'a20d3b07c'
    assert valid_data['party_id'] == 'a20d3b07c'

    # if any of the alias exist, the value will be populated for all of them, 
    # allowing you to use the one of your choice. However, ONE of them must exist:
    err = should_error(
                validation={'id': REQUIRED().alias('user_id', 'party_id').as_type(str) }, 
                user_data= {'user_name': 'susy'})
    assert "id = REQUIRED - Missing, Along with Aliases ['id', 'party_id', 'user_id']" in err 

    # also, other REQUIRED validations also apply:
    err = should_error(
                validation={'id':REQUIRED().alias('user_id', 'party_id').as_type(str) }, 
                user_data= {'party_id': 1234})
    assert "id = REQUIRED - Wrong Type (requires str, not int)" in err 

    # IMPORTANT NOTE ON ALIASES:
    # If you supply N aliases to a REQUIRED key (for N+1 options total) 
    # and only 1 exists, all others are added with the same value:
    valid_data = REQUIRED.validate_data(  keys_lowercased=False,
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'A': 42} )
    assert valid_data['A'] == valid_data['B'] == valid_data['C'] == valid_data['D'] \
                           == valid_data['E'] == valid_data['F'] == valid_data['G'] 
    
    # In this scenario, all options are treated equal, i.e., original key and all aliases become B
    valid_data = REQUIRED.validate_data(  keys_lowercased=False,
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'B': 42} )
    assert valid_data['B'] == valid_data['A'] == valid_data['C'] == valid_data['D'] \
                           == valid_data['E'] == valid_data['F'] == valid_data['G'] 
    
    # If the REQUIRED field (A) is found IN ADDITION to another alias (C) with 
    # has a DIFFERENT value, then
    # - the REQUIRED field (A) is considered the MAIN field, aka 'right' answer, 
    #   and all other MISSING keys are added and set to A.  i.e.,
    valid_data = REQUIRED.validate_data(  keys_lowercased=False,
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'A': 42, 'C': 37} )
    assert valid_data['A'] == valid_data['B'] == valid_data['D'] == valid_data['E'] \
                           == valid_data['F'] == valid_data['G'] == 42
    assert valid_data['C'] == 37

    # If the REQUIRED field (A) is MISSING AND two-or-more other aliases exist,
    # there is no way for this module to determine which is the "correct" value.
    # By default, will put the found aliases in alpha order and pick the first found.
    # In this scenario, it will also raise a WARNING to the calling program.
    valid_data = REQUIRED.validate_data(  keys_lowercased=False,
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'D': 42, 'C': 37, 'G': 197} )
    assert valid_data['A'] == valid_data['B'] == valid_data['C'] \
                           == valid_data['E'] == valid_data['F'] == 37
    assert valid_data['D'] == 42
    assert valid_data['G'] == 197
    
    wrn = should_warn(
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'D': 42, 'C': 37, 'G': 197} ) 
    assert 'Multiple alias values provided, but no master found. Picking first one: 37' in wrn
     
    # This is only a problem if the values are different - if they're the same, 
    # no warning is thrown (because it doesn't matter):
    valid_data = REQUIRED.validate_data(  keys_lowercased=False,
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'D': 42, 'C': 42, 'G': 42} )
    assert valid_data['A'] == valid_data['B'] == valid_data['C'] == valid_data['D'] \
                           == valid_data['E'] == valid_data['F'] == valid_data['G'] == 42

    wrn = should_warn( failmsg="This would detect a warning, if thrown, but there were no warnings.",
            validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
            user_data={'D': 42, 'C': 42, 'G': 42} )
    assert 'This would detect a warning, if thrown, but there were no warnings.' in wrn


    # If you would prefer to ERROR rather than arbitrarily pick the first value
    # you can set that preference in either 
    # - REQUIRED().alias('a', 'b', 'c', error_on_conflicting_aliases=True) 
    # - REQUIRED.validate_data( validation, user_data, error_on_conflicting_aliases=True)
    # Setting in either place will trigger errors rather than warnings. 

    # set at validation time (per validation, all columns):
    err = should_error( error_on_conflicting_aliases=True, 
                validation={'A': REQUIRED().alias('B','C','D','E','F','G')},
                user_data={'D': 42, 'C': 37, 'G': 197} )
    assert 'Multiple, conflicting aliases found, with no original validation field found.' in err

    # set at definition time (per column, all validations):
    err = should_error( error_on_conflicting_aliases=True, 
                validation={'A': REQUIRED().alias('B','C','D','E','F','G', error_on_conflicting_aliases=True)},
                user_data={'D': 42, 'C': 37, 'G': 197} )
    assert 'Multiple, conflicting aliases found, with no original validation field found.' in err

    # ----------------------------------------
    # Other Type Validation: 

    # let's break the email validation:
    err = should_error(
            validation = {'user_email': REQUIRED().as_email()},
            user_data =  {'user_email': 'jon@example,com'} ) # note the comma, not period
    assert 'user_email = REQUIRED - Present, but Not Valid Email Format (jon@example,com)' in err

    # let's break the Timestamp validation
    err = should_error(
            validation = {'joined_time': REQUIRED().as_isotime()},
            user_data  = {'joined_time': '2025-02-30T00:00:00+00:00'} ) # there is no Feb 30th:
    assert 'joined_time = REQUIRED - Present, but Not Valid ISO-8601 Time Format (2025-02-30T00:00:00+00:00)' in err
 
    # BTW, the validation dict is just a dict, so new elements can be added any time:
    validation = {'id': REQUIRED().as_type(int).as_posnum()}
    user_data  = {'id': 123}
    
    validation['user_choice'] = REQUIRED().constrain_to('A', 'B', 'C').default('C')
    assert REQUIRED.validate_data(validation, user_data)

    # constrain limits valid values to a set list.  
    # Conversely, you can also add a whitelist, which are values that are ALWAYS valid, 
    # regardless of other validation rules.
    validation['user_choice'] = REQUIRED().constrain_to('A', 'B', 'C').default('C').whitelist('Z')
    assert REQUIRED.validate_data(validation, {**user_data, 'user_choice': 'Z'})

    # whitelisted values override all checks EXCEPT missing key or None check
    validation['user_uuidv7'] = REQUIRED().as_uuid(7).whitelist('new','old','refused')
    assert REQUIRED.validate_data(validation, {**user_data, 'user_uuidv7': 'new'})
    assert REQUIRED.validate_data(validation, {**user_data, 'user_uuidv7': 'old'})
    assert REQUIRED.validate_data(validation, {**user_data, 'user_uuidv7': 'refused'})
    
    err = should_error(validation=validation, user_data={**user_data, 'user_uuidv7': 'suck it'})
    assert 'user_uuidv7 = REQUIRED - Present, but Not Valid UUID v7 format (suck it)' in err 

 
    # this will FAIL validation, because col1 is missing from user_data
    # The validation none_ok != missing key ok. 
    # If missing key is OK, just leave it out of the validation dict entirely.
    # There is nothing here that prevents non-validated keys in the user_data.
    try:
        pytest.raises(ValueError, 
                        REQUIRED().validate_data(
                            validation={
                                'id': REQUIRED().as_type(int), 
                                'col1': REQUIRED().none_ok() # none_ok != missing key ok, this will fail validation
                            },
                            user_data={'id': 12345}
                        ) 
                    )
    except ValueError as e:
        print(f'\n{e}') # returns user-friendly error message
        assert 'col1 = REQUIRED - Missing' in str(e)

    
    # this will PASS validation, because .default(None) will set missing keys to the default,
    # and because none_ok.  That said, entries for col1 and col2 are functionally the same;
    # col1 and col2 will be set to None if missing from user_data.
    assert          REQUIRED().validate_data(
                        validation={
                            'id': REQUIRED().as_type(int), 
                            'col1': REQUIRED().none_ok().default(None),
                            'col2': None
                        },
                        user_data={'id': 12345}
                    ) 
                

    # this will FAIL validation, because col1 will default to None if key missing,
    # but None is not typically allowed as a valid supplied type.
    try:
        pytest.raises(ValueError, 
                        REQUIRED().validate_data(
                            validation={
                                'id': REQUIRED().as_type(int), 
                                'col1': REQUIRED().default(None),
                                'col2': None
                            },
                            user_data={'id': 12345}
                        ) 
                    )
    except ValueError as e:
        print(f'\n{e}') # returns user-friendly error message
        assert 'col1 = REQUIRED - Present, but Empty' in str(e)



    # this will PASS validation:
    assert          REQUIRED().validate_data(
                        validation={
                            'email1': REQUIRED().as_email(), 
                            'email2': REQUIRED().as_email(),
                            'email3': REQUIRED().as_email(),
                            'email4': REQUIRED().as_email(),
                            'email5': REQUIRED().as_email(),
                            'email6': REQUIRED().as_email(),
                        },
                        user_data={
                            'email1': 'susy@cheese.com' ,
                            'email2': 'Amy@ExAmpLe.Org',
                            'email3': 'Bobby.12345@company.co',
                            'email4': 'johnny-storm@f4.gov',
                            'email5': 'Desi@some-really-long_name.zone',
                            'email6': 'geek.y.guy@192.168.1.1.com',
                            'email7': 'doesnt matter, not validated'
                        }
                    ) 


    # this will FAIL validation, due to various malformed email examples.  
    # Note that validation will fail 
    try:
        pytest.raises(ValueError, 
                        REQUIRED().validate_data(
                        validation={
                            'email1': REQUIRED().as_email(), 
                            'email2': REQUIRED().as_email(),
                            'email3': REQUIRED().as_email(),
                            'email4': REQUIRED().as_email(),
                            'email5': REQUIRED().as_email(),
                            'email6': None,
                        },
                        user_data={
                            'email1': 'susy.creamcheese@yummy.com.' , # trailing period
                            'email2': 'Amy.Org', # missing @
                            'email3': 'Bobby.12345@company.c', # TLD <2 chars
                            'email4': '@f4.gov', # recipient missing
                            'email5': 'Desi@.com', # domain misisng
                        }
                    )
        ) 
    except ValueError as e:
        print(f'\n{e}') # returns user-friendly error message
        assert 'email1 = REQUIRED - Present, but Not Valid Email Format (susy.creamcheese@yummy.com.)' in str(e)
        assert 'email2 = REQUIRED - Present, but Not Valid Email Format (Amy.Org)' in str(e)
        assert 'email3 = REQUIRED - Present, but Not Valid Email Format (Bobby.12345@company.c)' in str(e)
        assert 'email4 = REQUIRED - Present, but Not Valid Email Format (@f4.gov)' in str(e)
        assert 'email5 = REQUIRED - Present, but Not Valid Email Format (Desi@.com)' in str(e)


    # The library doesn't check whether validations are mutually exclusive,
    # allowing you to set tests whereby the validation will NEVER be valid.  
    # Because all checks are performed, multiple failures should all appear
    # in the valueerror message.
    try:
        pytest.raises(ValueError, 
                        REQUIRED().validate_data(
                            validation={
                                'id': REQUIRED().as_type(int).as_type(str), # can never pass
                                'col1': REQUIRED().as_posnum().as_negnum(), # 0 is only option here 
                                'col2': REQUIRED().as_uuid().as_isotime(), # can never pass
                                'col3': REQUIRED().as_json().as_email() # can never pass
                            },
                            user_data={'id': True,
                                       'col1': 123,
                                       'col2': 'my value',
                                       'col3': 'my value'
                                       }
                        ) 
                    )
    except ValueError as e:
        print(f'\n{e}') # returns user-friendly error message
        assert "  id = REQUIRED - Wrong Type (requires int, not bool)" in str(e)
        assert "  id = REQUIRED - Wrong Type (requires str, not bool)" in str(e)
        assert "col1 = REQUIRED - Present, but Not a Negative Number (123)" in str(e)
        assert "col2 = REQUIRED - Present, but Not Valid ISO-8601 Time Format (my value)" in str(e)
        assert "col2 = REQUIRED - Present, but Not Valid UUID format (my value) " in str(e)
        assert "col3 = REQUIRED - Present, but Not Valid Email Format (my value)" in str(e)
        assert "col3 = REQUIRED - Present, but Not Valid JSON format (my value)" in str(e)


    # By default, the as_type() compares actual types.  If you prefer to validate whether
    # your value isinstance of your supplied type, use the isinstance flag = True:
    assert REQUIRED().validate_data(
                validation={'id': REQUIRED().as_type(int, isinstance=True)},
                user_data={'id': True}) 
    # this passes because bool is an instance of int, aka isinstance(True, int) == True
    # immediately abov we didn't set isinstance flag, so it threw the validation error:
    #    id = REQUIRED - Wrong Type (requires int, not bool)
    

    # Note that the REQUIRED in the field definition need to be an instanace,
    # aka 'id': REQUIRED()   and not the class, aka  'id': REQUIRED
    # however validate_data() is a class function, so can be called either 
    # as a class or instance (aka with or without parens).

    assert REQUIRED().validate_data({'id': REQUIRED()}, {'id': 123}) # instance call
    assert REQUIRED.validate_data({'id': REQUIRED()}, {'id': 123}) # class call also works


    # also important to note: by default this will change all keys to str().lower()
    # and trim all string values.   This is light-weight dict cleaning, but can be disabled if needed.
    
    # Most important to note, the returned data (dict) will have all keys lowercased:
    assert REQUIRED.validate_data(validation = {'id': REQUIRED()}, user_data = {'ID': '123'}) # by default this will work, desipte the mixed case
    assert REQUIRED.validate_data(validation = {'id': REQUIRED()}, user_data = {'iD': '123'}) # by default this will work, desipte the mixed case
    assert REQUIRED.validate_data(validation = {'id': REQUIRED()}, user_data = {'Id': '123'}) # by default this will work, desipte the mixed case

    # you can easily disable this behavior using the keys_lowercased flag:
    try:
        pytest.raises(ValueError, REQUIRED().validate_data(
                                                validation={'id': REQUIRED()}, 
                                                user_data ={'ID': '123'},
                                                keys_lowercased=False) 
        )
    except ValueError as e:
        print(f'\n{e}') # returns user-friendly error message
        assert "id = REQUIRED - Missing" in str(e)

    
    # less invasive, the process will strip() all string values (ignoring non-strings):

    user_data = {'ID': '123 '} # note the extra space
    rtn_data = REQUIRED.validate_data(validation = {'id': REQUIRED()}, user_data = user_data ) # note the extra space
    assert user_data['ID'] != rtn_data['id'] # user_data still has whitespace, whereas rtn_data is stripped()
    assert user_data['ID'].strip() == rtn_data['id'] == '123'  
    
    # you can disable all of this behavior:
    rtn_data = REQUIRED.validate_data(validation = {'id': REQUIRED()}, 
                                      user_data  = {'ID': '123 '}, 
                                      values_trimmed=False)
    assert user_data['ID'] == rtn_data['id'] # rtn_data preserved the whitespace

    pass

test_required()