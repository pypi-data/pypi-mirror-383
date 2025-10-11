
local var,cid,n = "RPC"..plugin.mainDeviceId,plugin.mainDeviceId,0
local vinit,path = { name=var, value=""},"/plugins/"..cid.."/variables/"..var

api.post("/plugins/"..cid.."/variables",{ name=var, value=""}) -- create var if not exist
function fibaro._rpc(id,fun,args,timeout,qaf)
  n = n + 1
  api.put(path,vinit)
  fibaro.call(id,"RPC_CALL",path,var,n,fun,args,qaf)
  timeout = os.time()+(timeout or 3)
  while os.time() < timeout do
    local r,_ = api.get(path)
    if r and r.value~="" then
      r = r.value 
      if r[1] == n then
        if not r[2] then error(r[3],3) else return select(3,table.unpack(r)) end
      end
    end 
  end
  error(string.format("RPC timeout %s:%d",fun,id),3)
end

function fibaro.rpc(id,name,timeout) return function(...) return fibaro._rpc(id,name,{...},timeout) end end

function QuickApp:RPC_CALL(path2,var2,n2,fun,args,qaf)
  local res
  if qaf then res = {n2,pcall(self[fun],self,table.unpack(args))}
  else res = {n2,pcall(_G[fun],table.unpack(args))} end
  api.put(path2,{name=var2, value=res}) 
end