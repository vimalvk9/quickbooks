export class AppController {
  constructor($state) {
    this.$state = $state;
  }

  goHome() {
    this.$state.go("accountList");
  }
}