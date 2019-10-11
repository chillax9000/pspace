Vue.component('modal', {
    template: '#modal-template',
    data: function () {
        return {
          text: '',
          pk: null,
        };
    },
    methods: {
        close: function () {
            this.$emit('close');
            this.text = '';
        },
    }
})

Vue.component('daily', {
    methods: {
        getTimeStr(transaction) {
            return moment(transaction.time).format('DD MMM[,] H[h]mm')
        },
        getName(user_id, users) {
            for (user of users) {
                if (user.id == user_id)
                    return user.username;
            }
            return "unknown (" + user_id + ")";
        },
        getDirectionStr(transaction, users) {
            if (transaction.source == users.me.id) {
                return ' >> ' + this.getName(transaction.destination, users.contacts);
            } else if (transaction.destination == users.me.id) {
                return  ' << ' + this.getName(transaction.source, users.contacts);
            } else {
                return "???";
            }
        },
        getAmountStyle(transaction, users) {
            if (transaction.source == users.me.id) {
                color = "Tomato";
            } else if (transaction.destination == users.me.id) {
                color =  "MediumSeaGreen";
            } else {
                color = "Gray";
            }
            return {color: color, background: "white", width: "10%"};
        },
    },
    props: ["transaction", "users"],
    template: `
    <table class="main_table" style="border: 2px solid #eeeeee; color: Gray; background: #eeeeee">
        <tr>
            <td rowspan="2" v-bind:style="getAmountStyle(transaction, users)"> {{ transaction.amount }} </td>
            <td style="text-align: left"> {{ getDirectionStr(transaction, users) }} </td>
            <td colspan="2" style="text-align: right"> {{ getTimeStr(transaction) }} </td>
        </tr>
        <tr>
            <td style="width: 80%"> {{ transaction.text }} </td>
            <td> </td>
            <td style="width: 10%" @click="$emit('showmodify', transaction.id)"> {{ transaction.status }} </td>
        </tr>
    </table>
    `
})

Vue.component('recap', {
    data: function () {
        return {
          sum: 0
        }
    },
    methods: {
        computeSum(transactions, users) {
            sum = 0;
            for (transaction of transactions) {
                if (transaction.source == users.me.id) {
                coeff = -1
                } else if (transaction.destination == users.me.id) {
                    coeff = 1
                } else {
                    return "???";
                }
                sum += transaction.amount * coeff
            }
            this.sum = sum
            return sum
        },
        getSumStyle(sum) {
            if (sum > 0) {
                color =  "MediumSeaGreen";
            } else if (sum < 0) {
                color = "Tomato";
            } else {
                color = "Gray";
            }
            return {color: color};
        },
    },
    props: ["transactions", "users"],
    template: `
    <table class="main_table" style="border: 1px solid #eeeeee">
        <tr>
            <td v-bind:style="getSumStyle(sum)"> {{ computeSum(transactions, users) }}</td>
        </tr>
    </table>
    `
})
new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        transactions: [],
        users: {},
        text: '',
        other: 1,
        amount: 0,
        showNewModal: false,
        showModifyModal: false,
        direction: 1,
        pk: null,
    },
    methods: {
        getAll: function () {
            axios
              .get('/lbcflba/api/all')
              .then(response => (this.transactions = response.data))
              .catch(error => printerr("getAll::transactions"));
            axios
              .get('/lbcflba/api/contacts/all')
              .then(response => (this.users = response.data))
              .catch(error => printerr("getAll::contacts"));
        },
        newTransaction: function () {
            axios.post('/lbcflba/api/new',
                       {'other': this.other, 'text': this.text, 'amount': this.amount, 'direction': this.direction},
                       {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getAll()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.text = '';
                this.showNewModal = false;
            });
        },
        deleteTransaction: function () {
            axios.post('/lbcflba/api/delete', {'pk': this.pk}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getAll()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.pk = null;
                this.showModifyModal = false;
            });
        },
        test: function () {
            alert("testing testing");
        },
        printerr: function (err_msg) {
            alert("fail...\n" + err_msg);
        },
    },
    mounted() {
        this.getAll();
    }
})