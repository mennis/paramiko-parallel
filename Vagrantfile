# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'virtualbox'
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ruby-concurrency/oracle-solaris-11"
  config.vm.synced_folder ".", "/vagrant", create: true, enabled: true, id: "vagrant-root"


  config.vm.provider "virtualbox" do |v|
    v.gui = false
    v.memory = 4096
    v.cpus = 4
    config.ssh.insert_key = false
  end

end