const AttackLogger = artifacts.require("AttackLogger");

module.exports = function (deployer) {
  deployer.deploy(AttackLogger);
};