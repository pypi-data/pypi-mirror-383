from datetime import datetime
import json, logging, re, warnings


class REQUIRED(): 
    required:bool = True

    req_alias:list = []
    req_constraints:list = []
    req_type:list = []
    req_type_isinstance:bool = False
    req_whitelist:list = []
    req_default = None
    req_default_flag:bool = False
    req_email:bool = False
    req_isotime:bool = False
    req_json:bool = False
    req_noneok:bool = False
    req_negnum:bool = False
    req_posnum:bool = False
    req_num_gt:float = None
    req_num_gte:bool = False
    req_num_lt:float = None
    req_num_lte:bool = False
    req_uuid:bool = False
    req_uuid_version:int = None

    error_on_conflicting_aliases:bool = False
    class ConflictWarning(UserWarning): pass

    def __init__(self):
        self.req_type:list = []
    def __isnum__(self, value):
        value = str(value)
        if re.match(r'^[+-]?(\d+\.?\d*|\.\d+)$', value): 
            return float(value) if '.' in value else int(value)
        else: raise ValueError(f"Value must be numeric. Value: {value}")

    def as_type(self, required_type, isinstance=False):
         """Requires value to match the supplied type."""
         self.req_type.append(required_type); self.req_type_isinstance = isinstance; return self
    def as_isotime(self): 
        """Requires string values to be ISO-8601 (international standard) timestamp format."""
        self.req_isotime = True; return self
    def as_json(self): 
        """Requires string value to be valid json format."""
        self.req_json = True; return self
    def as_posnum(self): 
        """Requires value to be numeric and positive."""
        self.req_posnum = True; return self
    def as_negnum(self): 
        """Requires value to be numeric and netagive."""
        self.req_negnum = True; return self
    def greater_than(self, value, or_equal_to:bool = False):
        """Requires value to be numeric and greater than supplied value."""
        self.req_num_gt = self.__isnum__(value)
        self.req_num_gte = or_equal_to
        return self
    def less_than(self, value, or_equal_to:bool = False):
        """Requires value to be numeric and less than supplied value."""
        self.req_num_lt = self.__isnum__(value)
        self.req_num_lte = or_equal_to
        return self
    def as_email(self):
        """Requires value to be a valid email address format."""
        self.req_email = True; return self
    def as_uuid(self, version:int=None): 
        """Requires string value to be standard UUID format (8-4-4-4-12 hex, i.e. RFC 4122/RFC 9562). 
        Optionally, you can constrain to a specific UUID Version with an integer version number. Version = None will match any."""
        self.req_uuid = True; self.req_uuid_version = version; return self
    def whitelist(self, *values): 
        """Allows for certain 'whitelist' values to always pass validation."""
        self.req_whitelist = values; return self
    def none_ok(self): 
        """Allows None values as valid (typically disallowed)."""
        self.req_noneok = True; return self
    def constrain_to(self, *constraints): 
        """Requires value to match one of the supplied values."""
        self.req_constraints = list(constraints); return self
    def alias(self, *alias_name, error_on_conflicting_aliases:bool = False): 
        """Requires any ONE key exist from a supplied list of keys. If all keys are missing / not set, validation fails. If ANY of the keys are set, validation will create any missing and set them all to the same value."""
        self.error_on_conflicting_aliases = error_on_conflicting_aliases
        self.req_alias = alias_name; return self
    def default(self, value=None): 
        """Sets a default value to use if missing."""
        self.req_default_flag=True
        self.req_default = value
        return self

    def __str__(self):
        if not self.required: return 'REQUIREMENT DISBALED, NO VALIDATION.'
        rtn =                                          ["REQUIRED: KEY MUST EXIST"]
        if self.req_alias != []           : rtn.append(f"REQUIRED: alias : " + str(self.req_alias))
        if self.req_isotime != False      : rtn.append(f"REQUIRED: isotime : " + str(self.req_isotime ))
        if self.req_json != False         : rtn.append(f"REQUIRED: json : " + str(self.req_json ))
        if self.req_type != []            : rtn.append(f"REQUIRED: type : " + str(self.req_type) + f" (strict: {self.req_type_isinstance})" )
        if self.req_default_flag != False : rtn.append(f"REQUIRED: default_flag : " + str(self.req_default_flag ))
        if self.req_default != None       : rtn.append(f"REQUIRED: default : " + str(self.req_default ))
        if self.req_posnum != False       : rtn.append(f"REQUIRED: posnum : " + str(self.req_posnum ))
        if self.req_negnum != False       : rtn.append(f"REQUIRED: negnum : " + str(self.req_negnum ))
        if self.req_uuid != False         : rtn.append(f"REQUIRED: uuid : " + str(self.req_uuid ))
        if self.req_uuid_version != None  : rtn.append(f"REQUIRED: uuid_version : " + str(self.req_uuid_version ))
        if self.req_constraints != []     : rtn.append(f"REQUIRED: constraints : " + str(self.req_constraints ))
        if self.req_noneok != False       : rtn.append(f"REQUIRED: noneok : " + str(self.req_noneok ))
        if self.req_whitelist != []       : rtn.append(f"REQUIRED: whitelist : " + str(self.req_whitelist ))
        if self.req_email != False        : rtn.append(f"REQUIRED: email : " + str(self.req_email ))
        return '  \n'.join(rtn)
    
    @classmethod
    def validate_data(cls, validation:dict, user_data:dict, 
                    keys_lowercased=True, values_trimmed=True,
                    error_on_missing_required:bool = True,
                    error_on_conflicting_aliases:bool = False) -> dict:
        """Applies previously assigned validations between a dictionary providing the validation source, and a user supplied dataset.
        
        It will also perform light-weight normalization of the user dict by enforcing all keys to be lowercase strings, 
        and trimming / stripping all whitespace from string values (ignoring non-strings). Both of these behaviors can be turned off.

        This is a class method, and can be called with or without an instance of the class. 
        Output is a validated dict object.  Any validation failures throw a ValueError.
        """
        def __trimifstr__(value, values_trimmed:bool):
            if values_trimmed and isinstance(value, str): return value.strip()
            else: return value
        def __lowerifstr__(value, keys_lowercased:bool):
            if keys_lowercased and isinstance(value, str): return value.lower()
            else: return value

        maxkeylen = max([len(k) for k in user_data.keys()]+[len(k) for k in validation.keys()])
        user_data   = {__lowerifstr__(k, keys_lowercased): __trimifstr__(v, values_trimmed) for k, v in user_data.items()} 
        validation =  {__lowerifstr__(k, keys_lowercased): __trimifstr__(v, values_trimmed) for k, v in validation.items()} 
        allrealdata = { **{k:v for k,v in validation.items() if not isinstance(v, REQUIRED)}, **user_data}
        required = {k:v for k,v in validation.items() if isinstance(v, REQUIRED)} 
        missing = []
        
        for k,v in required.items():

            # Apply default if needed:
            if v.req_default_flag and (k not in allrealdata or not allrealdata[k]): 
                allrealdata[k] = v.req_default

            # do aliases first, since they alone can adjust the dictionary items:
            if v.req_alias:
                aliases = [k, *sorted([__lowerifstr__(a, keys_lowercased) for a in v.req_alias])]
                if v.none_ok: found = [a for a in aliases if a in allrealdata]
                else:         found = [a for a in aliases if a in allrealdata and allrealdata[a]]
                if not found: 
                    missing.append( f"{k.rjust(maxkeylen)} = " + f'REQUIRED - Missing, Along with Aliases {aliases}')
                    continue
                elif len(found) == 1: 
                    for a in aliases: allrealdata[a] = allrealdata[found[0]]
                else: # found multiple, now the fun begins: 
                    if k in found:  # this is considered the MAIN, make all missing aliases this value:
                        for alias in [a for a in aliases if a not in allrealdata]: allrealdata[alias] = allrealdata[k]
                    else:  # no MAIN found, just pick the first one and make all missing aliases this value:
                        firstvalue = allrealdata[found[0]]
                        if not all([allrealdata[f]==firstvalue for f in found]): # there is some mix of non-MAIN values, we need to warn the user:
                            warnings.warn(f"Multiple alias values provided, but no master found. Picking first one: {firstvalue}", cls.ConflictWarning)
                        if error_on_conflicting_aliases or v.error_on_conflicting_aliases: 
                            raise ValueError(f"Multiple, conflicting aliases found, with no original validation field found.")
                        # if no error, then proceed with the first found (alphabetically):
                        for alias in [a for a in aliases if a not in allrealdata]: allrealdata[alias] = firstvalue
                    
            # Basic Test: missing or empty?
            if k not in allrealdata: 
                missing.append( f"{k.rjust(maxkeylen)} = " + 'REQUIRED - Missing')
                continue
            elif v.req_noneok and allrealdata[k] is None:
                continue # if none_ok, then none is ok
            elif allrealdata[k] in v.req_whitelist:
                continue # if whitelisted, then it's ok, regardless of anything else
            elif allrealdata[k] is None: 
                missing.append( f"{k.rjust(maxkeylen)} = " + 'REQUIRED - Present, but Empty')
                continue

            # Constraint Test
            if v.req_constraints:
                test_constraints = [*v.req_constraints, None] if v.req_noneok else v.req_constraints
                if allrealdata[k] not in test_constraints:
                    missing.append( f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Present, but Not in Defined Constraints [{v.req_constraints}] ({allrealdata[k]})")

            # ------------------------------------------------------------

            # Type Test
            for reqtype in v.req_type:
                if v.req_type_isinstance: 
                    if not isinstance(allrealdata[k], reqtype): 
                        missing.append( f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Wrong Type (requires {reqtype.__name__}, not {type(allrealdata[k]).__name__})")
                else:
                    if not type(allrealdata[k]) == reqtype: 
                        missing.append( f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Wrong Type (requires {reqtype.__name__}, not {type(allrealdata[k]).__name__})")
            
            # Email Format Test
            if v.req_email:
                email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$')
                if not bool(email_pattern.match(allrealdata[k])): 
                    missing.append( f"{k.rjust(maxkeylen)} = " + f'REQUIRED - Present, but Not Valid Email Format ({allrealdata[k]})')

            # Positive number test
            if v.req_posnum:
                try: 
                    tmp_num = float(allrealdata[k])
                    if tmp_num < 0: raise Exception
                except: missing.append( f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Present, but Not a Positive Number ({allrealdata[k]})")

            # Negative number test
            if v.req_negnum:
                try: 
                    tmp_num = float(allrealdata[k])
                    if tmp_num > 0: raise Exception
                except: missing.append( f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Present, but Not a Negative Number ({allrealdata[k]})")

            # Greater than test
            if v.req_num_gt is not None:
                try: 
                    if v.req_num_gte:
                        if allrealdata[k] < v.req_num_gt: raise Exception
                    else: 
                        if allrealdata[k] <= v.req_num_gt: raise Exception
                except: missing.append(f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Present, but Not Greater Than {f'or Equal To' if v.req_num_gte else ''}{v.req_num_gt} ({allrealdata[k]})")

            # Less than test
            if v.req_num_lt is not None:
                try:
                    if v.req_num_lte:
                        if allrealdata[k] > v.req_num_lt: raise Exception
                    else:
                        if allrealdata[k] >= v.req_num_lt: raise Exception
                except: missing.append(f"{k.rjust(maxkeylen)} = " + f"REQUIRED - Present, but Not Less Than {f'or Equal To' if v.req_num_lte else ''}{v.req_num_lt} ({allrealdata[k]})")
                

            # ISO Time Format Test
            if v.req_isotime:
                try: tmp_ts = datetime.fromisoformat(allrealdata[k].replace('Z', '+00:00'))
                except: missing.append( f"{k.rjust(maxkeylen)} = " + f'REQUIRED - Present, but Not Valid ISO-8601 Time Format ({allrealdata[k]})')

            # JSON Format Test
            if v.req_json:
                try:
                    if type( allrealdata[k] ) == dict: pass # always OK
                    elif type( allrealdata[k] ) == str: tmp_json = json.loads( allrealdata[k] )
                    else: tmp_json = json.loads( str(allrealdata[k]) )
                except: missing.append( f"{k.rjust(maxkeylen)} = " + f'REQUIRED - Present, but Not Valid JSON format ({allrealdata[k]})')
            
            # UUID Format Test
            if v.req_uuid:
                version_part = f"{v.req_uuid_version}[0-9a-f]{{3}}" if v.req_uuid_version else "[0-9a-f]{4}"
                version_part = version_part + ('-[cd]' if v.req_uuid_version == 2 else '-[89ab]')
                full_pattern = rf"^[0-9a-f]{{8}}-[0-9a-f]{{4}}-{version_part}[0-9a-f]{{3}}-[0-9a-f]{{12}}$"
                uuid7_pattern = re.compile(full_pattern, re.IGNORECASE)
                if not bool(uuid7_pattern.match(allrealdata[k])): 
                    missing.append( f"{k.rjust(maxkeylen)} = " + f'REQUIRED - Present, but Not Valid UUID{" v"+ str(v.req_uuid_version) if v.req_uuid_version else ""} format ({str(allrealdata[k])})')


        # Report and Error if needed
        if missing and error_on_missing_required:
            errmsg = [f"\n\nOne or more required fields were missing, left empty, or of the wrong type:"]
            errmsg.append('  \n'.join(missing))
            errmsg.append("\nFull signature (JSON keys):")
            errmsg.append("  Required:  " + ', '.join( [f"{k} ({', '.join(v.req_alias)})" if v.req_alias else k for k,v in required.items()  if not v.req_default] ))
            errmsg.append("  Optional:  " + ', '.join( [k for k,v in validation.items() if (isinstance(v, REQUIRED) and v.req_default) or k not in required.keys()] ))
            logging.error(f"🔥 Missing required field: {', '.join(missing)}")
            raise ValueError('\n'.join(errmsg))
        # No error, return combined dictionary
        return allrealdata


