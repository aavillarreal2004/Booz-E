%ID Number Getter

function nummy = numID(ID)
    if matches(ID, '')
        nummy = 0;
    else
        nummy = str2double(extractAfter(ID, 2));
    end
end