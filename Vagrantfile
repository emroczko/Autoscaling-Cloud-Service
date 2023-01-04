Vagrant.configure("2") do |config|
  config.vm.define "web01" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.101"
    web.vm.provision "shell", path: "install_web.sh", args: "web01"
  end

  config.vm.define "web02" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.102"
    web.vm.provision "shell", path: "install_web.sh", args: "web02"
  end

  config.vm.define "web03" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.103"
    web.vm.provision "shell", path: "install_web.sh", args: "web03"
  end
end
