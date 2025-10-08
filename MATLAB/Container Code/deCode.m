%Decoder

function decode = deCode(ID)
    run("DataParser.m")
    if extract(ID, 1) == "D"
        decode = recipes(str2double(erase(ID, "D-"))).name;
    elseif extract(ID, 1) == "I"
        decode = ingredients(str2double(erase(ID, "I-"))).name;
    end
end