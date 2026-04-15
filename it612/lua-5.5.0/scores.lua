local scores = {88, 94, 71, 76, 91}

for i, score in ipairs(scores) do
    print(i, score)
end

local student = {name = "alice", lab = 19, passed = true}

for key, value in pairs(student) do
    print(key, value)
end